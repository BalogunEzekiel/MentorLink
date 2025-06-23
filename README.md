
# Mentorship Matching Platform (Streamlit + Supabase)

## Setup
1. Install dependencies:
```
pip install -r requirements.txt
```

2. Add a `.env` file using `.env.example` as template.

3. Run the app:
```
streamlit run app.py
```

## Supabase Tables
- `users`: userid, email, password, role
- `profile`: profileid, userid, bio, skills, goals
- `availability`: availabilityid, mentored, date, start, end
- `mentorshiprequest`: mentorshiprequestid, menteeid, mentorid, status, createdat
- `session`: sessionid, mentorid, menteeid, date, feedback, rating
