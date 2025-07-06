import uuid
import bcrypt
from database import supabase  # ✅ Ensure this path is correct

def setup_admin_account():
    admin_accounts = [
        {
            "email": "admin01@theincubatorhub.com",
            "password": "Admin01@123",
            "role": "Admin I"
        },
        {
            "email": "admin02@theincubatorhub.com",
            "password": "Admin02@123",
            "role": "Admin II"
        }
    ]

    for admin in admin_accounts:
        try:
            # 🔍 Check if the admin already exists
            existing = supabase.table("users").select("*").eq("email", admin["email"]).execute()
            if existing.data:
                print(f"ℹ️ Admin account already exists: {admin['email']}")
                continue

            # 🔐 Hash the password securely
            hashed_pw = bcrypt.hashpw(admin["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            # 🆕 Create the admin user
            supabase.table("users").insert({
                "userid": str(uuid.uuid4()),
                "email": admin["email"],
                "password": hashed_pw,
                "role": admin["role"],
                "must_change_password": False,
                "profile_completed": True,
                "status": "Active"
            }).execute()

            print(f"✅ Admin account created: {admin['email']} as {admin['role']}")

        except Exception as e:
            print(f"🔥 Failed to create admin account {admin['email']}: {e}")
