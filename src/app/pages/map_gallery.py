import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_leaflet as dl
from auth import get_supabase_client

dash.register_page(__name__, path="/gallery", title="Vadvilág - Térkép és Galéria")

layout = html.Div(
    className="gallery-page",
    children=[
        dcc.Location(id="gallery-redirect", refresh=True),
        html.Div(id="gallery-content", className="gallery-container")
    ]
)

@callback(
    Output("gallery-content", "children"),
    Output("gallery-redirect", "href"),
    Input("auth-store", "data")
)
def render_gallery(auth_data):
    """
    Lekéri az összes észlelési adatot a Supabase-ből, és megjeleníti a térkép- és galéria elrendezést.
    
    Args:
        auth_data (dict): Felhasználói munkamenet adatok a hitelesített adatbázis-hozzáféréshez.
        
    Returns:
        tuple: (gallery_page_layout, redirect_path)
    """
    if not auth_data or not auth_data.get("access_token"):
        return no_update, "/login"

    try:
        access_token = auth_data.get("access_token")
        sb = get_supabase_client(access_token)
        # Összes feltöltés lekérése
        res = sb.table("user_uploads").select("*").execute()
        uploads = res.data
    except Exception as e:
        uploads = []
        print(f"Hiba a feltöltések lekérésekor: {e}")

    markers = []
    gallery_items = []
    
    for upload in uploads:
        ul_id = upload.get("id")
        lat = upload.get("latitude")
        lon = upload.get("longitude")
        c_name = upload.get("predicted_class")
        conf = upload.get("confidence", 0) * 100 if upload.get("confidence") else 0
        img_data = upload.get("image_data")
        
        if lat is not None and lon is not None:
            markers.append(
                dl.Marker(
                    position=[lat, lon],
                    id={"type": "map-marker", "index": ul_id},
                    children=[
                        dl.Tooltip(f"{c_name} ({conf:.1f}%)")
                    ]
                )
            )
            
        gallery_items.append(
            html.Div(
                className="gallery-item glass-card",
                id={"type": "gallery-item", "index": ul_id},
                children=[
                    html.Img(src=img_data, className="gallery-img", style={"width": "100%", "height": "150px", "objectFit": "cover", "borderRadius": "8px"}),
                    html.H4(c_name, style={"marginTop": "10px", "color": "#2ecc71"}),
                    html.P(f"Konfidencia: {conf:.1f}%", style={"margin": "0", "fontSize": "12px", "color": "#95a5a6"}),
                    html.P(f"Helyszín: {lat:.3f}, {lon:.3f}", style={"margin": "0", "fontSize": "12px", "color": "#bdc3c7"}),
                ],
                style={"padding": "10px", "marginBottom": "15px", "cursor": "pointer"}
            )
        )

    return html.Div([
        html.H1("Klasszifikált Állatok Térképe", style={"textAlign": "center", "marginBottom": "20px"}),
        html.Div(
            style={"display": "flex", "height": "70vh", "gap": "20px", "flexWrap": "wrap"},
            children=[
                # Térkép szekció (Bal oldal)
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "borderRadius": "12px", "overflow": "hidden", "boxShadow": "0 8px 32px 0 rgba(31, 38, 135, 0.37)"},
                    children=[
                        dl.Map(center=[47.4979, 19.0402], zoom=6, children=[
                            dl.TileLayer(),
                            dl.FeatureGroup(id="markers-group", children=markers)
                        ], style={'width': '100%', 'height': '100%', 'zIndex': 1})
                    ]
                ),
                
                # Részletek és Galéria szekció (Jobb oldal)
                html.Div(
                    style={"flex": "1", "minWidth": "300px", "display": "flex", "flexDirection": "column", "gap": "10px"},
                    children=[
                        html.H3("Kiválasztott Kép", style={"margin": "0"}),
                        html.Div(id="selected-image-details", className="glass-card", style={"padding": "15px", "minHeight": "200px", "display": "flex", "alignItems": "center", "justifyContent": "center", "color": "#7f8c8d"}),
                        html.H3("Összes Kép", style={"marginTop": "20px", "marginBottom": "10px"}),
                        html.Div(
                            className="gallery-scroll",
                            style={"overflowY": "auto", "flex": "1", "paddingRight": "10px"},
                            children=gallery_items
                        )
                    ]
                )
            ]
        ),
        # Tároló a feltöltések adatainak
        dcc.Store(id="uploads-data", data=uploads)
    ]), no_update


@callback(
    Output("selected-image-details", "children"),
    Input({"type": "map-marker", "index": dash.ALL}, "n_clicks"),
    Input({"type": "gallery-item", "index": dash.ALL}, "n_clicks"),
    State("uploads-data", "data"),
    prevent_initial_call=True
)
def update_selected_details(marker_clicks, gallery_clicks, uploads):
    """
    Frissíti a részletes nézetet, amikor egy észlelést kiválasztanak a térképen vagy a galériában.
    
    Args:
        marker_clicks (list): Kattintási események a térkép jelölőkről.
        gallery_clicks (list): Kattintási események a galéria elemekről.
        uploads (list): Az észlelési rekordok listája az adatkereséshez.
        
    Returns:
        html.Div: Részletes nézet tartalma (kép, faj, konfidencia, helyszín).
    """
    ctx = dash.callback_context
    if not ctx.triggered or not uploads:
        return "Kattints egy markerre vagy képre a részletekért."
        
    prop_id = ctx.triggered[0]["prop_id"]
    try:
        import json
        clicked_id_dict = json.loads(prop_id.split(".")[0])
        clicked_id = clicked_id_dict["index"]
    except:
        return "Hiba a kiválasztás során."
        
    for upload in uploads:
        if upload.get("id") == clicked_id:
            c_name = upload.get("predicted_class")
            conf = upload.get("confidence", 0) * 100 if upload.get("confidence") else 0
            img_data = upload.get("image_data")
            lat = upload.get("latitude")
            lon = upload.get("longitude")
            
            return html.Div([
                html.Img(src=img_data, style={"width": "100%", "maxHeight": "250px", "objectFit": "contain", "borderRadius": "8px"}),
                html.H3(c_name, style={"marginTop": "15px", "color": "#2ecc71"}),
                html.P(f"Konfidencia: {conf:.1f}%"),
                html.P(f"Koordináták: {lat:.5f}, {lon:.5f}")
            ])
            
    return "Kattints egy markerre vagy képre a részletekért."
