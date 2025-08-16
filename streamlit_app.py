import streamlit as st
from datetime import datetime

# ---------------------------- PAGE CONFIG ----------------------------
st.set_page_config(
    page_title="AI Epidemic Triage Assistant",
    page_icon="🧬",
    layout="wide"
)

# ---------------------------- STYLING ----------------------------
# Add gradient background & custom design with CSS
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #e0f7fa 0%, #f1f8e9 100%);
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
.big-title {
    font-size: 40px !important;
    font-weight: 700;
    color: #004d40;
    text-align: center;
    margin-bottom: 10px;
}
.subtitle {
    font-size: 18px !important;
    color: #00695c;
    text-align: center;
    margin-bottom: 30px;
}
.result-box {
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
}
.result-green {
    background: #e8f5e9;
    border-left: 6px solid #2e7d32;
}
.result-yellow {
    background: #fffde7;
    border-left: 6px solid #fbc02d;
}
.result-red {
    background: #ffebee;
    border-left: 6px solid #c62828;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ---------------------------- SAFETY DISCLAIMER ----------------------------
DISCLAIMER = """
**⚠️ Safety Notice (Prototype Only)**  
This tool is for **demonstration and educational purposes only**.  
It is **not** a medical device, does **not** diagnose, and must not replace medical care.  
If you have severe symptoms (e.g., trouble breathing, chest pain, confusion, severe dehydration, uncontrolled bleeding) seek **emergency care immediately**.
"""

# ---------------------------- KNOWLEDGE BASE ----------------------------
DISEASES = {
    "COVID-19 / Influenza-like illness (ILI)": {
        "symptoms": {"fever", "cough", "sore_throat", "runny_nose", "fatigue", "headache",
                     "myalgia", "loss_smell_taste", "shortness_breath"},
        "context": {"close_contact_sick", "outbreak_local", "crowded_indoor"},
        "red_flags": {"shortness_breath", "confusion", "chest_pain"},
        "prevention": ["Wear a mask in crowded spaces", "Ventilate rooms", "Wash hands often"],
        "home_care": ["Rest, hydrate", "Isolate until no fever for 24h", "Monitor breathing"],
    },
    "Dengue (mosquito-borne)": {
        "symptoms": {"fever", "headache", "retro_orbital_pain", "myalgia", "arthralgia", "nausea", "vomiting", "rash"},
        "context": {"mosquito_bites", "outbreak_local", "recent_travel_tropic"},
        "red_flags": {"bleeding", "severe_abdominal_pain", "persistent_vomiting"},
        "prevention": ["Avoid mosquito bites", "Use repellents and nets", "Eliminate standing water"],
        "home_care": ["Hydrate well", "Avoid NSAIDs unless prescribed", "Watch for bleeding"],
    },
    "Gastroenteritis / Cholera risk": {
        "symptoms": {"diarrhea", "vomiting", "abdominal_pain", "fever"},
        "context": {"unsafe_water_food", "outbreak_local"},
        "red_flags": {"severe_dehydration", "blood_in_stool"},
        "prevention": ["Drink safe water", "Wash hands before meals", "Eat hygienic food"],
        "home_care": ["Oral rehydration (ORS)", "Rest", "Seek help if unable to drink fluids"],
    }
}

SYMPTOMS_LIST = [
    ("fever", "Fever"),
    ("cough", "Cough"),
    ("sore_throat", "Sore throat"),
    ("runny_nose", "Runny nose"),
    ("fatigue", "Fatigue"),
    ("headache", "Headache"),
    ("myalgia", "Muscle pain"),
    ("loss_smell_taste", "Loss of smell/taste"),
    ("shortness_breath", "Shortness of breath"),
    ("chest_pain", "Chest pain"),
    ("confusion", "Confusion"),
    ("retro_orbital_pain", "Pain behind eyes"),
    ("arthralgia", "Joint pain"),
    ("nausea", "Nausea"),
    ("vomiting", "Vomiting"),
    ("diarrhea", "Diarrhea"),
    ("abdominal_pain", "Abdominal pain"),
    ("bleeding", "Bleeding"),
    ("severe_abdominal_pain", "Severe abdominal pain"),
    ("blood_in_stool", "Blood in stool"),
]

EXPOSURES = [
    ("close_contact_sick", "Contact with sick person"),
    ("crowded_indoor", "Crowded indoor spaces"),
    ("outbreak_local", "Local outbreak present"),
    ("mosquito_bites", "Frequent mosquito bites"),
    ("recent_travel_tropic", "Recent travel to tropics"),
    ("unsafe_water_food", "Unsafe food/water consumption"),
]

# ---------------------------- FUNCTIONS ----------------------------
def compute_scores(selected_symptoms, selected_exposures):
    scores = {}
    for disease, meta in DISEASES.items():
        s_overlap = len(meta["symptoms"].intersection(selected_symptoms))
        c_overlap = len(meta["context"].intersection(selected_exposures))
        scores[disease] = s_overlap * 2 + c_overlap
    max_score = max(scores.values()) if scores else 1
    return {k: int((v / max_score) * 100) for k, v in scores.items()}

def triage(selected_symptoms):
    if {"shortness_breath", "chest_pain", "confusion", "severe_abdominal_pain"} & selected_symptoms:
        return "Emergency", "Immediate hospital/emergency care needed."
    elif {"fever", "vomiting", "diarrhea"} & selected_symptoms and len(selected_symptoms) > 3:
        return "Urgent (within 24h)", "See a doctor within 24 hours."
    else:
        return "Home care", "Monitor symptoms, hydrate, rest. Seek help if worsening."

# ---------------------------- UI ----------------------------
st.markdown('<p class="big-title">🧬 Epidemic Triage Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">An AI-powered prototype to ask health questions, assess epidemic symptoms, and suggest safe next steps.</p>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966480.png", width=120)
    st.markdown("### ℹ️ About this App")
    st.write("This app is a **prototype AI assistant** that:")
    st.write("- Asks about your symptoms & exposures")
    st.write("- Compares them with known epidemic patterns")
    st.write("- Suggests **safe next steps (not diagnosis)**")
    st.info("💡 Made for **research & educational demo**")
    st.markdown("---")
    st.warning(DISCLAIMER)

st.subheader("👤 Your Information")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", min_value=0, max_value=120, value=25)
with col2:
    days_sick = st.number_input("Days unwell", min_value=0, max_value=30, value=1)

st.subheader("🌍 Exposures")
chosen_exposures = st.multiselect("Select exposures", [label for _, label in EXPOSURES])
exposure_keys = {key for key, label in EXPOSURES if label in chosen_exposures}

st.subheader("🤒 Symptoms")
cols = st.columns(2)
selected_symptoms = set()
for i, (key, label) in enumerate(SYMPTOMS_LIST):
    with cols[i % 2]:
        if st.checkbox(label, key=f"s_{key}"):
            selected_symptoms.add(key)

if st.button("🔍 Analyze"):
    if not selected_symptoms:
        st.warning("Please select symptoms first.")
    else:
        scores = compute_scores(selected_symptoms, exposure_keys)
        level, advice = triage(selected_symptoms)

        # TRIAGE RESULT
        st.subheader("📊 Triage Result")
        if level == "Emergency":
            st.markdown(f'<div class="result-box result-red"><h4>🚨 {level}</h4><p>{advice}</p></div>', unsafe_allow_html=True)
        elif level.startswith("Urgent"):
            st.markdown(f'<div class="result-box result-yellow"><h4>⚠️ {level}</h4><p>{advice}</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="result-box result-green"><h4>✅ {level}</h4><p>{advice}</p></div>', unsafe_allow_html=True)

        # POSSIBLE MATCHES
        st.subheader("🦠 Possible Matches")
        for disease, pct in scores.items():
            st.write(f"**{disease}** — match score: {pct}%")
            with st.expander(f"See prevention & care for {disease}"):
                st.write("**Prevention:**")
                for p in DISEASES[disease]["prevention"]:
                    st.write(f"- {p}")
                st.write("**Home care:**")
                for h in DISEASES[disease]["home_care"]:
                    st.write(f"- {h}")

        st.caption(f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
