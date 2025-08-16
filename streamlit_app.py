import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Epidemic Triage Prototype", page_icon="🩺", layout="centered")

# ----------------------------- SAFETY DISCLAIMER -----------------------------
DISCLAIMER = """
**Safety Notice (Prototype Only)**  
This tool is for demonstration and educational purposes. It is **not** a medical device,
does **not** provide diagnosis or medical advice, and must not be used for emergencies.
If you have severe symptoms (e.g., trouble breathing, chest pain, confusion, severe dehydration,
uncontrolled bleeding) seek **emergency care immediately**.
"""

# ----------------------------- SIMPLE RULE SET -----------------------------
# Each "disease" has: core symptoms, context flags, red flag combos, and general advice
DISEASES = {
    "COVID-19 / Influenza-like illness (ILI)": {
        "symptoms": {
            "fever", "cough", "sore_throat", "runny_nose", "fatigue", "headache",
            "myalgia", "loss_smell_taste", "shortness_breath"
        },
        "context": {"close_contact_sick", "outbreak_local", "crowded_indoor"},
        "red_flags": {"shortness_breath", "confusion", "chest_pain", "persistent_high_fever"},
        "prevention": [
            "Wear a well-fitted mask around others",
            "Improve ventilation, avoid crowded indoor spaces",
            "Hand hygiene; cover cough/sneeze"
        ],
        "home_care": [
            "Rest and fluids",
            "Monitor temperature and breathing",
            "Isolate from others while symptomatic"
        ],
        "for_clinician": [
            "Consider rapid antigen/RT-PCR (COVID-19) or flu testing where appropriate",
            "Consider pulse oximetry if available"
        ]
    },
    "Dengue (mosquito-borne)": {
        "symptoms": {"fever", "headache", "retro_orbital_pain", "myalgia", "arthralgia", "nausea", "vomiting", "rash"},
        "context": {"mosquito_bites", "outbreak_local", "recent_travel_tropic"},
        "red_flags": {"bleeding", "severe_abdominal_pain", "persistent_vomiting", "mucosal_bleed", "lethargy"},
        "prevention": [
            "Avoid mosquito bites: repellents, long sleeves, screens",
            "Reduce standing water around home"
        ],
        "home_care": [
            "Rest and oral hydration",
            "Avoid NSAIDs unless advised by a clinician",
            "Look for warning signs (bleeding, severe pain, persistent vomiting)"
        ],
        "for_clinician": [
            "CBC/platelets, hematocrit trend; consider dengue testing per local protocol"
        ]
    },
    "Acute gastroenteritis / Cholera-like dehydration risk": {
        "symptoms": {"diarrhea", "vomiting", "abdominal_pain", "fever"},
        "context": {"unsafe_water_food", "outbreak_local"},
        "red_flags": {"severe_dehydration", "blood_in_stool", "persistent_vomiting"},
        "prevention": [
            "Safe water/food hygiene",
            "Handwashing after toilet and before food prep"
        ],
        "home_care": [
            "Oral rehydration solution (ORS) sips frequently",
            "Seek care if unable to keep fluids down"
        ],
        "for_clinician": [
            "Assess dehydration; stool testing where indicated; electrolytes if available"
        ]
    }
}

SYMPTOMS_LIST = [
    ("fever", "Fever ≥38°C"),
    ("cough", "Cough"),
    ("sore_throat", "Sore throat"),
    ("runny_nose", "Runny or congested nose"),
    ("fatigue", "Unusual fatigue"),
    ("headache", "Headache"),
    ("myalgia", "Muscle aches"),
    ("loss_smell_taste", "Loss of smell/taste"),
    ("shortness_breath", "Shortness of breath"),
    ("chest_pain", "Chest pain/pressure"),
    ("confusion", "New confusion/difficulty waking"),
    ("retro_orbital_pain", "Pain behind the eyes"),
    ("arthralgia", "Joint pain"),
    ("nausea", "Nausea"),
    ("vomiting", "Vomiting"),
    ("diarrhea", "Diarrhea"),
    ("abdominal_pain", "Abdominal pain"),
    ("bleeding", "Bleeding gums/nose/skin bruising"),
    ("mucosal_bleed", "Mucosal bleed"),
    ("severe_abdominal_pain", "Severe abdominal pain"),
    ("persistent_vomiting", "Persistent vomiting"),
    ("blood_in_stool", "Blood in stool"),
]

EXPOSURES = [
    ("close_contact_sick", "Close contact with a sick person in last 14 days"),
    ("crowded_indoor", "Time spent in crowded/poorly ventilated indoor settings"),
    ("outbreak_local", "Known local outbreak/epidemic alerts"),
    ("mosquito_bites", "Frequent mosquito bites recently"),
    ("recent_travel_tropic", "Travel to tropical/subtropical region recently"),
    ("unsafe_water_food", "Possibly unsafe water or food consumed recently"),
]

COMORBIDITIES = [
    "Pregnancy", "Diabetes", "Hypertension", "Heart disease",
    "Chronic lung disease/asthma", "Kidney disease",
    "Liver disease", "Immunocompromised"
]

# ----------------------------- UTILS -----------------------------
def red_flag_present(selected_symptoms, dehydration_flags):
    rf = {"shortness_breath", "confusion", "chest_pain", "bleeding",
          "mucosal_bleed", "severe_abdominal_pain", "persistent_vomiting"}
    if dehydration_flags.get("severe_dehydration"):
        rf.add("severe_dehydration")
    return any(s in rf for s in selected_symptoms) or dehydration_flags.get("severe_dehydration", False)

def compute_scores(selected_symptoms, selected_exposures):
    scores = {}
    for disease, meta in DISEASES.items():
        s_overlap = len(meta["symptoms"].intersection(selected_symptoms))
        c_overlap = len(meta["context"].intersection(selected_exposures))
        scores[disease] = s_overlap * 2 + c_overlap  # simple weighting: symptoms more important
    # Normalize to 0-100 for nicer display
    max_score = max(scores.values()) if scores else 1
    for k in scores:
        scores[k] = int(round((scores[k] / max_score) * 100)) if max_score > 0 else 0
    return dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))

def care_level(selected_symptoms, dehydration_flags, days_sick, comorbid_count):
    # Simple, explainable triage bands
    if red_flag_present(selected_symptoms, dehydration_flags):
        return "Emergency", [
            "Seek emergency care immediately.",
            "Do not delay; call local emergency number or go to the nearest ER."
        ]
    # Prolonged high fever or worsening symptoms → urgent
    if ("fever" in selected_symptoms and days_sick >= 3) or \
       ("shortness_breath" in selected_symptoms) or \
       (dehydration_flags.get("moderate_dehydration") and days_sick >= 1):
        return "Urgent evaluation (same-day/24h)", [
            "Arrange in-person clinical evaluation within 24 hours.",
            "If symptoms worsen, go to emergency care."
        ]
    # Higher risk due to comorbidities
    if comorbid_count >= 2 and ("fever" in selected_symptoms or "cough" in selected_symptoms):
        return "Prompt clinic visit (48h)", [
            "Book a clinic visit within 48 hours and monitor closely."
        ]
    # Mild
    return "Home care with monitoring", [
        "Rest, fluids, and monitor symptoms.",
        "If symptoms persist/worsen or new red flags appear, seek care."
    ]

# ----------------------------- UI -----------------------------
st.title("🩺 Epidemic Triage – Minimal Prototype")
st.caption("Ask about medical history, exposure, and symptoms; produce non‑diagnostic, safety‑first guidance.")

with st.expander("Read first: Safety disclaimer", expanded=False):
    st.info(DISCLAIMER)

st.subheader("👤 Basic info")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age (years)", min_value=0, max_value=120, value=30)
with col2:
    days_sick = st.number_input("How many days have you felt unwell?", min_value=0, max_value=30, value=1)

st.subheader("🧬 Medical history (select any that apply)")
chosen_comorbid = st.multiselect("Comorbidities / special situations", COMORBIDITIES)
comorbid_count = len(chosen_comorbid)

st.subheader("🌍 Exposure & epidemic
