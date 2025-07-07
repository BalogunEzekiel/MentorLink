import uuid
import bcrypt
from database import supabase  # ✅ Ensure this path is correct


def setup_admin_account():
    admin_email = "admin@theincubatorhub.com"
    admin_password = "Admin@123"
    admin_role = "Admin"

    try:
        # 🔍 Check if the admin account already exists
        existing = supabase.table("users").select("*").eq("email", admin_email).execute()
        if existing.data:
            print("ℹ️ Admin account already exists.")
            return

        # 🔐 Hash the password securely
        hashed_pw = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # 🆕 Create the admin user
        supabase.table("users").insert({
            "userid": str(uuid.uuid4()),
            "email": admin_email,
            "password": hashed_pw,
            "role": admin_role,
            "must_change_password": False,
            "profile_completed": True,
            "status": "Active"
        }).execute()

        print("✅ Admin account successfully created.")

    except Exception as e:
        print("🔥 Failed to create admin account:", e)
