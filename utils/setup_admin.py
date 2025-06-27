import uuid
import bcrypt
from supabase.client import supabase

def setup_admin_account():
    admin_email = "admin@theincubatorhub.com"
    admin_password = "Admin@123"
    admin_role = "Admin"

    result = supabase.table("users").select("*").eq("email", admin_email).execute()
    if result.data:
        return  # Admin already exists

    hashed_pw = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        supabase.table("users").insert({
            "userid": str(uuid.uuid4()),
            "email": admin_email,
            "password": hashed_pw,
            "role": admin_role,
            "must_change_password": False,
            "profile_completed": True
        }).execute()
        print("✅ Admin account created.")
    except Exception as e:
        print("🔥 Failed to insert admin account:", e)
