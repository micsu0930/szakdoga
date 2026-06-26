# Supabase autentikációs segédmodul.
import os
from supabase import create_client, Client, ClientOptions


def get_supabase_client(access_token: str = None) -> Client:
    """
    Inicializálja és visszaadja a Supabase klienst.
    
    Args:
        access_token (str, optional): A felhasználó hozzáférési tokenje a hitelesített kérésekhez.
            Ha meg van adva, a kliens tartalmazni fogja a tokent az Authorization fejlécben.
            
    Returns:
        Client: Egy Supabase kliens példány.
    """
    url = os.getenv("SUPABASE_URL", "http://kong:8000")
    key = os.getenv("SUPABASE_KEY", "")
    if access_token:
        return create_client(url, key, options=ClientOptions(headers={'Authorization': f'Bearer {access_token}'}))
    return create_client(url, key)

# regisztráció
def sign_up(email: str, password: str) -> dict:
    """
    Új felhasználót regisztrál a Supabase Auth segítségével.
    
    Args:
        email (str): A felhasználó email címe.
        password (str): Az új fiók jelszava.
        
    Returns:
        dict: Egy szótár, amely tartalmazza a 'success' állapotot, egy üzenetet a felületnek, 
              és a felhasználói adatokat sikeres regisztráció esetén.
    """

    try:
        client = get_supabase_client()
        response = client.auth.sign_up({
            "email": email,
            "password": password,
        })

        if response.user:
            return {
                "success": True,
                "message": "Sikeres regisztráció! Mostmár bejelentkezhet",
                "data": {
                    "user_id": response.user.id,
                    "email": response.user.email,
                },
            }
        return {
            "success": False,
            "message": "Sikertelen regisztráció. Próbálja újra.",
        }

    except Exception as e:
        error_msg = str(e)
        if "already" in error_msg.lower() or "exists" in error_msg.lower():
            return {"success": False, "message": "ehhez az email-hez már tartozik fiók"}
        if "password" in error_msg.lower():
            return {"success": False, "message": "A jelszónak legalább 6 karakteresnek kell lennie."}
        return {"success": False, "message": f"Regisztrációs hiba: {error_msg}"}


def sign_in(email: str, password: str) -> dict:
    """
    Hitelesíti a felhasználót email és jelszó használatával.
    
    Args:
        email (str): A felhasználó email címe.
        password (str): A felhasználó jelszava.
        
    Returns:
        dict: Egy szótár, amely tartalmazza a 'success' állapotot, egy üzenetet, és a 
              munkamenet tokeneket sikeres bejelentkezés esetén.
    """

    try:
        client = get_supabase_client()
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if response.session:
            return {
                "success": True,
                "message": "Sikeres bejelentkezés!",
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "user_email": response.user.email,
                    "user_id": response.user.id,
                },
            }
        return {
            "success": False,
            "message": "Sikertelen bejelentkezés. Ellenőrizze az adatait",
        }

    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "credentials" in error_msg.lower():
            return {"success": False, "message": "Érvénytelen email vagy jelszó."}
        return {"success": False, "message": f"Bejelentkezési hiba: {error_msg}"}


def sign_out(access_token: str) -> dict:
    """
    Kijelentkezteti a felhasználót a jelenlegi munkamenetből.
    
    Args:
        access_token (str): A felhasználó aktív hozzáférési tokenje.
        
    Returns:
        dict: Az állapot jelzi a sikert.
    """

    try:
        client = get_supabase_client()
        client.auth.sign_out()
        return {"success": True, "message": "Sikeres kijelentkezés!"}
    except Exception:
        # ha a szerver oldali kijelentkezés sikertelen, akkor is sikeresnek jelöljük a lokális kijelentkezést
        return {"success": True, "message": "Sikeres kijelentkezés!"}
