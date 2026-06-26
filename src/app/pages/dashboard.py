import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_leaflet as dl
import io
import base64
import os
from auth import get_supabase_client
try:
    import numpy as np
    from PIL import Image
except ImportError:
    pass

try:
    import tensorflow as tf
    MODEL_PATH = "/app/wildlife_classifier_final.keras"
except ImportError:
    tf = None
    MODEL_PATH = ""

model = None

try:
    from classes import CLASS_NAMES
except ImportError:
    CLASS_NAMES = []

dash.register_page(__name__, path="/dashboard", title="Vadvilág - Dashboard")

layout = html.Div(
    className="dashboard-page",
    children=[
        dcc.Location(id="dashboard-redirect", refresh=True),

        html.Div(
            id="dashboard-content",
            className="dashboard-container",
        ),
    ],
)


@callback(
    Output("dashboard-content", "children"),
    Output("dashboard-redirect", "href"),
    Input("auth-store", "data"),
)
def render_dashboard(auth_data):
    """
    Megjeleníti a védett dashboard tartalmat a hitelesített felhasználók számára.
    
    Args:
        auth_data (dict): Hitelesítési munkamenet adatai.
        
    Returns:
        tuple: (dashboard_layout, redirect_path)
    """

    if not auth_data or not auth_data.get("access_token"):
        return no_update, "/login"

    # Statisztikák lekérése az adatbázisból
    total_class = "0"
    last_val = "—"
    total_ul = "0"
    
    try:
        user_id = auth_data.get("user_id")
        access_token = auth_data.get("access_token")
        sb = get_supabase_client(access_token)
        res = sb.table("user_stats").select("*").eq("user_id", user_id).execute()
        if res.data:
            stats = res.data[0]
            total_class = str(stats.get("total_classified", 0))
            last_val = stats.get("last_class", "—")
            # Az összes feltöltéshez használhatunk egy oszlopot vagy megszámolhatjuk a user_uploads bejegyzéseket
            # Itt megszámoljuk a bejegyzéseket a pontosság érdekében
            count_res = sb.table("user_uploads").select("id", count="exact").eq("user_id", user_id).execute()
            total_ul = str(count_res.count if count_res.count is not None else 0)
    except Exception as e:
        print(f"Hiba a statisztikák betöltésekor: {e}")

    return html.Div([
        html.Div(
            className="dashboard-header",
            children=[
                html.H1(
                    children=[
                        html.Span("Üdvözöljük, ", className="welcome-text"),
                        html.Span(auth_data.get("user_email", "User"), className="welcome-email"),
                    ],
                ),
                html.P("Your wildlife classification dashboard", className="dashboard-subtitle"),
            ],
        ),

        # Gyors statisztikák
        html.Div(
            className="dashboard-stats",
            children=[
                _dash_stat("", total_class, "Képek klasszifikálva", "stat-classified"),
                _dash_stat("", last_val, "Utolsó osztályozás", "stat-last"),
                _dash_stat("", total_ul, "Összes feltöltés", "stat-total"),
            ],
        ),

        # Upload section placeholder
        html.Div(
            className="upload-section glass-card",
            children=[
                html.H3("Kép klasszifikálása", style={"textAlign": "center"}),
                html.Div([
                    html.P("Állítsa be a készítés helyét a térképen:", style={"textAlign": "center"}),
                    dl.Map(center=[47.4979, 19.0402], zoom=6, children=[
                        dl.TileLayer(),
                        dl.LayerGroup(id="location-marker")
                    ], id="location-map", style={'width': '100%', 'height': '250px', "marginBottom": "10px", "borderRadius": "8px", "zIndex": 1}),
                    html.Div([
                        dcc.Input(id="upload-lat", type="number", placeholder="Szélesség (Lat)", style={"marginRight": "10px", "flex": "1", "padding": "5px"}),
                        dcc.Input(id="upload-lon", type="number", placeholder="Hosszúság (Lon)", style={"flex": "1", "padding": "5px"}),
                    ], style={"display": "flex", "justifyContent": "center", "marginBottom": "20px"}),
                ]),
                dcc.Upload(
                    id="upload-image",
                    children=html.Div([
                        "Húzd ide a képet, vagy ",
                        html.A("Kattints a kiválasztáshoz", style={"color": "#4a90e2", "cursor": "pointer"})
                    ]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderColor": "#4a90e2",
                        "borderRadius": "8px",
                        "textAlign": "center",
                        "marginBottom": "20px",
                        "backgroundColor": "rgba(255, 255, 255, 0.05)"
                    },
                    multiple=False,
                    accept="image/*"
                ),
                dcc.Loading(
                    id="loading-output",
                    type="circle",
                    color="#4a90e2",
                    children=html.Div(id="upload-output", style={"textAlign": "center", "minHeight": "200px"})
                )
            ],
        ),
    ]), no_update


@callback(
    Output("upload-output", "children"),
    Output("stat-classified", "children"),
    Output("stat-last", "children"),
    Output("stat-total", "children"),
    Input("upload-image", "contents"),
    State("upload-image", "filename"),
    State("stat-classified", "children"),
    State("stat-total", "children"),
    State("upload-lat", "value"),
    State("upload-lon", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True
)
def update_output(contents, filename, current_classified, current_total, lat, lon, auth_data):
    """
    Feldolgozza a feltöltött képet, lefuttatja az osztályozást, és elmenti az eredményeket az adatbázisba.
    
    Args:
        contents (str): Base64 kódolt kép tartalom.
        filename (str): A feltöltött fájl neve.
        current_classified (str): UI számláló az aktuális munkamenetben osztályozott képekhez.
        current_total (str): UI számláló az összes feltöltéshez.
        lat (float): A térképen kiválasztott földrajzi szélesség.
        lon (float): A térképen kiválasztott földrajzi hosszúság.
        auth_data (dict): Felhasználói munkamenet adatok az adatbázis mentéshez.
        
    Returns:
        tuple: (result_html, new_classified_count, predicted_label, new_total_count)
    """
    global model
    if contents is not None:
        
        try:
            total_uploads = int(current_total) + 1
        except (ValueError, TypeError):
            total_uploads = 1

        if tf is None:
            return html.Div("A Tensorflow nem tölthető be.", style={"color": "red"}), current_classified, "Hiba", str(total_uploads)
            
        if model is None and os.path.exists(MODEL_PATH):
            try:
                model = tf.keras.models.load_model(MODEL_PATH)
            except Exception as e:
                print(f"Hiba a modell betöltésekor: {e}")
                
        if model is None:
            return html.Div("Az MI modell fájl nem tölthető be, vagy nincs megfelelően csatolva.", style={"color": "red"}), current_classified, "Hiba", str(total_uploads)
        
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            img = Image.open(io.BytesIO(decoded)).convert('RGB')
            img_resized = img.resize((224, 224))
            img_array = np.array(img_resized)
            img_array = np.expand_dims(img_array, axis=0)
            
            preds = model.predict(img_array, verbose=0)
            class_idx = np.argmax(preds[0])
            confidence = float(np.max(preds[0]))
            
            if class_idx < len(CLASS_NAMES):
                class_name = CLASS_NAMES[class_idx].replace('_', ' ')
            else:
                class_name = f"Unknown ({class_idx})"
                
            try:
                new_classified = int(current_classified) + 1
            except (ValueError, TypeError):
                new_classified = 1

            # Mentés az adatbázisba, ha a koordináták és a hitelesítés jó
            db_msg = html.Div()
            user_id = auth_data.get("user_id") if auth_data else None
            if user_id and lat is not None and lon is not None:
                try:
                    # A méret csökkentése érdekében, ha a base64 túl nagy, újra kódolhatnánk kisebbre, de egyelőre közvetlenül mentjük.
                    # Egy max 800px-es korlát a tartalmon jó lenne, de most közvetlenül a bemeneti tartalmat mentjük.
                    access_token = auth_data.get("access_token")
                    sb = get_supabase_client(access_token)
                    sb.table("user_uploads").insert({
                        "user_id": user_id,
                        "image_data": contents,
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "predicted_class": class_name,
                        "confidence": confidence
                    }).execute()
                    db_msg = html.Div("Sikeresen mentve az adatbázisba!", style={"color": "#2ecc71", "marginTop": "10px", "fontWeight": "bold"})
                    
                    # Felhasználói statisztikák frissítése (Upsert)
                    try:
                        new_total_db = int(current_classified) + 1
                        sb.table("user_stats").upsert({
                            "user_id": user_id,
                            "total_classified": new_total_db,
                            "last_class": class_name,
                            "updated_at": "now()"
                        }).execute()
                    except Exception as se:
                        print(f"Statisztika frissítési hiba: {se}")
                        
                except Exception as e:
                    db_msg = html.Div(f"Adatbázis mentési hiba: {e}", style={"color": "#f39c12", "marginTop": "10px"})
            else:
                db_msg = html.Div("Kép klasszifikálva, de nincs adatbázisba mentve (hiányzó koordináta vagy bejelentkezés).", style={"color": "#95a5a6", "marginTop": "10px"})

            return html.Div([
                html.H3(f"Predikció: {class_name}", style={"color": "#2ecc71"}),
                html.H4(f"Konfidencia: {confidence * 100:.2f}%"),
                db_msg,
                html.Img(src=contents, style={"maxWidth": "100%", "maxHeight": "400px", "borderRadius": "8px", "marginTop": "20px"})
            ]), str(new_classified), class_name, str(total_uploads)
            
        except Exception as e:
            return html.Div(f"Hiba történt a feldolgozás során: {e}", style={"color": "red"}), current_classified, "Hiba", str(total_uploads)
    return html.Div(), current_classified, "—", current_total


def _dash_stat(icon: str, value: str, label: str, val_id: str = None):
    """
    Segédfüggvény egy statisztikai kártya komponens létrehozásához.
    
    Args:
        icon (str): Megjelenítendő ikon vagy emoji.
        value (str): A megjelenítendő elsődleges érték.
        label (str): Leíró címke szövege.
        val_id (str, optional): DOM ID az érték tárolójához a célzott frissítésekhez.
        
    Returns:
        html.Div: Egy Dash komponens a statisztikai kártyához.
    """
    return html.Div(
        className="dash-stat glass-card",
        children=[
            html.Div(icon, className="dash-stat-icon"),
            html.Div(value, className="dash-stat-value", id=val_id) if val_id else html.Div(value, className="dash-stat-value"),
            html.Div(label, className="dash-stat-label"),
        ],
    )

@callback(
    Output("upload-lat", "value"),
    Output("upload-lon", "value"),
    Output("location-marker", "children"),
    Input("location-map", "clickData"),
    prevent_initial_call=True
)
def update_location(clickData):
    """
    Frissíti a koordináta bemeneteket és a térkép jelölőt, amikor a felhasználó a térképre kattint.
    
    Args:
        clickData (dict): Adatok a térkép kattintási eseményéből, beleértve a latlng koordinátákat.
        
    Returns:
        tuple: (latitude, longitude, marker_component)
    """
    if clickData:
        lat = clickData['latlng']['lat']
        lon = clickData['latlng']['lng']
        marker = dl.Marker(position=[lat, lon])
        return lat, lon, [marker]
    return no_update, no_update, no_update

