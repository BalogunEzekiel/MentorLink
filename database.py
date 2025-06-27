# Connect to Supabase and define all DB interaction functions
#from supabase import create_client
from database import supabase  # ✅ Replace this with the correct import path
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Example: Get all mentors
def get_mentors():
    return supabase.table("users").select("*").eq("role", "Mentor").execute().data

# Example: Get user profile
def get_profile(userid):
    result = supabase.table("profile").select("*").eq("userid", userid).execute()
    return result.data[0] if result.data else None

# Example: Save availability
def save_availability(data):
    return supabase.table("availability").insert(data).execute()

# And more utility functions...
