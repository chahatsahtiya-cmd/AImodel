# app.py
# Streamlit Epidemic Diseases Q&A + Safe Guidance (non-diagnostic)
# Run: streamlit run app.py

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple
import datetime as dt

import streamlit as st

# ------------------------------
# Configuration & Styles
# ------------------------------
st.set_page_config(
    page_title="Epidemic Diseases Q&A (Safe Guidance Demo)",
    page_icon="🩺",
    layout="wide"
)

HIDE_FOOTER = """
<style>
footer {visibility: hidden;}
</style>
"""
st.markdown(HIDE_FOOTER, unsafe_allow_html=True)

# ------------------------------
# Safety & Disclaimers
# ------------------------------
DISCLAIMER = """
**Important Safety Notice**

- This app provides **general educational information only**. It is **not medical advice** and does **not diagnose** conditions.
- If you have symptoms or concerns, **consult a licensed healthcare professional**.
- **Seek urgent medical care immediately** if you have any **red-flag symptoms** (listed below).
"""

RED_FLAGS = [
    "Severe shortness of breath / difficulty breathing",
    "Blue/gray lips or face",
    "Severe chest pain or pressure",
    "Confusion, inability to wake or stay awake",
    "Seizures",
    "Severe dehydration (no urination, dizziness, fainting)",
    "Persistent high fever (> 39.4°C / 103°F) unresponsive to meds",
    "Signs of shock (cold clammy skin, rapid weak pulse)",
    "Severe bleeding / black or bloody stool / vomiting blood",
    "Severe abdominal pain",
    "Stiff neck with fever and rash (possible meningitis/measles complications)",
    "Any rapidly worsening symptom"
]

# ------------------------------
# Built-in Knowledge Base
# ------------------------------
@dataclass
class DiseaseInfo:
    name: str
    common_symptoms: List[str]
    incubation_days: str
    transmission: str
    key_tests: List[str]
    typical_course: str
    supportive_care: List[str]
    treatment_notes_safe: List[str]
    avoid_notes: List[str]
    prevention: List[str]
    red_flags_specific: List[str]
    keywords: List[str]

KB: Dict[str, DiseaseInfo] = {}

def add_disease(d: DiseaseInfo):
    KB[d.name.lower()] = d
    for k in d.keywords:
        KB[k.lower()] = d  # alias keywords -> disease

add_disease(DiseaseInfo(
    name="COVID-19",
    common_symptoms=["fever", "cough", "fatigue", "sore throat", "loss of taste or smell", "headache", "muscle aches", "congestion", "shortness of breath"],
    incubation_days="2–14 days (often 3–5)",
    transmission="Respiratory droplets/aerosols; close contact; shared indoor air",
    key_tests=["Rapid antigen test", "PCR test"],
    typical_course="Mild to moderate in most; risk higher with age, pregnancy, or comorbidities.",
    supportive_care=[
        "Hydration and rest",
        "Fever control (acetaminophen/paracetamol if not contraindicated)",
        "Masking and isolation per local guidance"
    ],
    treatment_notes_safe=[
        "High-risk individuals may be eligible for antivirals (clinician-prescribed).",
        "Monitor oxygen saturation if available; seek care if < 92–94% or worsening."
    ],
    avoid_notes=[
        "Avoid unnecessary antibiotics (viral illness)."
    ],
    prevention=[
        "Vaccination per local guidelines",
        "Ventilation, masking in crowded indoor settings",
        "Hand hygiene"
    ],
    red_flags_specific=[
        "Worsening shortness of breath",
        "Oxygen saturation < 92–94% on room air"
    ],
    keywords=["covid", "sars-cov-2", "coronavirus"]
))

add_disease(DiseaseInfo(
    name="Influenza",
    common_symptoms=["fever", "chills", "cough", "sore throat", "runny nose", "muscle aches", "headache", "fatigue"],
    incubation_days="1–4 days",
    transmission="Respiratory droplets/aerosols; contact with contaminated surfaces",
    key_tests=["Rapid influenza diagnostic test", "PCR"],
    typical_course="Abrupt onset; usually resolves in 3–7 days, fatigue may last longer.",
    supportive_care=[
        "Hydration, rest",
        "Acetaminophen/paracetamol for fever and pain if not contraindicated"
    ],
    treatment_notes_safe=[
        "Antivirals may be prescribed for high-risk patients if started early (clinician decision)."
    ],
    avoid_notes=["Avoid unnecessary antibiotics."],
    prevention=["Seasonal vaccination", "Respiratory etiquette"],
    red_flags_specific=["Shortness of breath", "Persistent high fever", "Chest pain", "Severe weakness"],
    keywords=["flu", "influenza"]
))

add_disease(DiseaseInfo(
    name="Dengue",
    common_symptoms=["fever", "severe headache", "pain behind the eyes", "muscle/joint pain", "nausea", "vomiting", "rash"],
    incubation_days="4–10 days",
    transmission="Aedes mosquitoes",
    key_tests=["NS1 antigen", "IgM/IgG serology", "PCR (early)"],
    typical_course="Febrile phase 2–7 days; may progress to critical phase (plasma leakage).",
    supportive_care=[
        "Hydration with oral rehydration solution (ORS)",
        "Acetaminophen/paracetamol for fever if not contraindicated",
        "Close monitoring for warning signs (abdominal pain, bleeding, lethargy)"
    ],
    treatment_notes_safe=[
        "No NSAIDs/aspirin (bleeding risk).",
        "Assess hematocrit/platelets in clinical care."
    ],
    avoid_notes=["Avoid ibuprofen, naproxen, aspirin."],
    prevention=["Eliminate standing water", "Mosquito repellents, nets, long sleeves"],
    red_flags_specific=["Bleeding", "Severe abdominal pain", "Persistent vomiting", "Lethargy/restlessness"],
    keywords=["dengue fever"]
))

add_disease(DiseaseInfo(
    name="Malaria",
    common_symptoms=["fever (often periodic)", "chills", "sweats", "headache", "nausea", "vomiting", "fatigue"],
    incubation_days="7–30+ days depending on species",
    transmission="Anopheles mosquitoes (parasite Plasmodium)",
    key_tests=["Rapid diagnostic test (RDT)", "Blood smear microscopy"],
    typical_course="Can be severe; P. falciparum may rapidly progress.",
    supportive_care=[
        "Hydration and fever control (acetaminophen if not contraindicated)"
    ],
    treatment_notes_safe=[
        "Requires clinician-prescribed antimalarials based on species/severity and local resistance.",
        "Urgent care for suspected severe malaria."
    ],
    avoid_notes=["Do not self-treat without testing and medical guidance."],
    prevention=["Repellents, nets", "Chemoprophylaxis for travelers when indicated"],
    red_flags_specific=["Confusion", "Seizures", "Severe anemia", "Jaundice", "Respiratory distress"],
    keywords=["plasmodium"]
))

add_disease(DiseaseInfo(
    name="Cholera",
    common_symptoms=["profuse watery diarrhea (rice-water stool)", "vomiting", "leg cramps", "thirst"],
    incubation_days="12 hours–5 days",
    transmission="Fecal-oral via contaminated water/food",
    key_tests=["Stool culture/rapid tests per local protocols"],
    typical_course="Can cause rapid dehydration and shock if untreated.",
    supportive_care=[
        "Immediate oral rehydration solution (ORS)",
        "Seek IV fluids for severe dehydration"
    ],
    treatment_notes_safe=[
        "Clinician may prescribe antibiotics in moderate/severe cases to reduce volume and duration."
    ],
    avoid_notes=["Avoid anti-diarrheals that reduce gut motility unless advised by a clinician."],
    prevention=["Safe water, sanitation, hand hygiene", "Oral cholera vaccines where available"],
    red_flags_specific=["Sunken eyes, very little/no urination, lethargy, weak pulse"],
    keywords=["vibrio cholerae"]
))

add_disease(DiseaseInfo(
    name="Measles",
    common_symptoms=["fever", "cough", "runny nose", "conjunctivitis", "Koplik spots", "rash (face → body)"],
    incubation_days="7–21 days",
    transmission="Highly contagious respiratory droplets/aerosols",
    key_tests=["Measles IgM serology", "PCR"],
    typical_course="Rash appears ~day 3–5 of illness; complications possible.",
    supportive_care=[
        "Hydration, rest",
        "Acetaminophen for fever if not contraindicated",
        "Vitamin A supplementation may be recommended by clinicians"
    ],
    treatment_notes_safe=[
        "Isolation to prevent spread.",
        "Monitor for pneumonia/encephalitis (seek care)."
    ],
    avoid_notes=["Avoid contact with unvaccinated and immunocompromised persons."],
    prevention=["MMR vaccination", "Isolation during infectious period"],
    red_flags_specific=["Breathing difficulty", "Persistent high fever", "Altered consciousness", "Seizures"],
    keywords=["rubeola"]
))

ALL_DISEASES = sorted({v.name for v in KB.values()})

# ------------------------------
# Helper Functions
# ------------------------------
def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())

def match_diseases_from_text(text: str, top_k: int = 3) -> List[Tuple[DiseaseInfo, int]]:
    tokens = tokenize(text)
    scores = []
    for disease in {v.name: v for v in KB.values()}.values():
        score = 0
        # symptom term overlap
        for s in disease.common_symptoms + disease.keywords:
            if any(t in s.lower() or s.lower() in t for t in tokens):
                score += 2
        # name hit
        if disease.name.lower() in text.lower():
            score += 3
        scores.append((disease, score))
    # sort by score desc, then by name
    scores.sort(key=lambda x: (-x[1], x[0].name))
    # filter zero scores unless no info typed
    if text.strip():
        scores = [s for s in scores if s[1] > 0]
    return scores[:top_k]

def assess_risk_level(user_red_flags: List[str]) -> str:
    return "Emergency—seek urgent care" if user_red_f
