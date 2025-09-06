# utils/matching.py

from typing import List, Dict
import re

# ---- Type definitions ----
class UserProfile:
    def __init__(self, user_id: str, role: str, bio: str, skills: List[str], goals: str):
        self.id = user_id
        self.role = role  # "mentor" or "mentee"
        self.bio = bio
        self.skills = skills
        self.goals = goals

# ---- Utility functions ----

def skill_score(mentee_skills: List[str], mentor_skills: List[str]) -> float:
    """Compute overlap of skills between mentee and mentor"""
    if not mentee_skills:
        return 0.0
    overlap = set(s.lower() for s in mentee_skills) & set(s.lower() for s in mentor_skills)
    return len(overlap) / len(mentee_skills)

def semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Very simple similarity based on word overlap.
    Later, replace with embeddings (OpenAI, HuggingFace, etc.) for better results.
    """
    if not text_a or not text_b:
        return 0.0
    words_a = set(re.findall(r"\w+", text_a.lower()))
    words_b = set(re.findall(r"\w+", text_b.lower()))
    if not words_a:
        return 0.0
    return len(words_a & words_b) / len(words_a)

def match_score(mentee: UserProfile, mentor: UserProfile) -> float:
    """Weighted score combining skills, goals, and bios"""
    s_score = skill_score(mentee.skills, mentor.skills)
    g_score = semantic_similarity(mentee.goals, mentor.bio + " " + " ".join(mentor.skills))
    b_score = semantic_similarity(mentee.bio, mentor.bio)

    score = 0.4 * s_score + 0.3 * g_score + 0.3 * b_score
    return round(min(max(score, 0.0), 1.0), 2)  # clamp between 0 and 1, 2 decimals

def recommend_mentors(mentee: UserProfile, mentors: List[UserProfile], top_n: int = 5) -> List[Dict]:
    """Return ranked mentors with score and shared skills"""
    results = []
    for mentor in mentors:
        if mentor.role != "mentor":
            continue
        score = match_score(mentee, mentor)
        shared_skills = list(
            set(s.lower() for s in mentee.skills) & set(s.lower() for s in mentor.skills)
        )
        results.append({
            "mentorId": mentor.id,
            "score": score,
            "sharedSkills": shared_skills,
            "bio": mentor.bio
        })
    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_n]
