#Supabase auth helper.
import os
from supabase import create_client, Client


def get_supabase_client() -> Client:
#Supabase client.
    url = os.getenv("SUPABASE_URL", "http://kong:8000")
    key = os.getenv("SUPABASE_KEY", "")
    return create_client(url, key)

#reg
def sign_up(email: str, password: str) -> dict:

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
        return {"success": False, "message": f"Registration error: {error_msg}"}


def sign_in(email: str, password: str) -> dict:

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
            return {"success": False, "message": "Invalid email or password."}
        return {"success": False, "message": f"Login error: {error_msg}"}


def sign_out(access_token: str) -> dict:

    try:
        client = get_supabase_client()
        client.auth.sign_out()
        return {"success": True, "message": "Sikeres kijelentkezés!"}
    except Exception:
        #if servers side fails logout
        return {"success": True, "message": "Sikeres kijelentkezés!"}
