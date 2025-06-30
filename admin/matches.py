import streamlit as st
from database import supabase
from utils.session_creator import create_session_if_available
from googleapiclient.discovery import build
from emailer import send_email
from datetime import datetime, timedelta

def show():
    st.subheader("🔁 Match & Book Sessions")

    users = supabase.table("users").select("userid,email,role").neq("status","Delete").execute().data
    mentors = [u for u in users if u["role"]=="Mentor"]
    mentees = [u for u in users if u["role"]=="Mentee"]

    mentee = st.selectbox("Mentee", [m["email"] for m in mentees])
    mentor = st.selectbox("Mentor", [m["email"] for m in mentors])
    if st.button("Create Match"):
        m_id = next(u["userid"] for u in mentees if u["email"]==mentee)
        t_id = next(u["userid"] for u in mentors if u["email"]==mentor)
        exist = supabase.table("mentorshiprequest").select("*").eq("menteeid",m_id).eq("mentorid",t_id).execute().data
        if exist:
            st.warning("Already exists")
        else:
            res = supabase.table("mentorshiprequest").insert({
                "menteeid":m_id,"mentorid":t_id,"status":"ACCEPTED"
            }).execute()
            req_id = res.data[0]["mentorshiprequestid"]
            start = datetime.utcnow()
            end = start + timedelta(minutes=30)
            success, msg = create_session_if_available(supabase,t_id,m_id,start,end, send_email=True)
            st.success("Session booked!" if success else msg)

