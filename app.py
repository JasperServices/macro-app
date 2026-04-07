import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

# ======================
# FIREBASE INIT
# ======================
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ======================
# DOELEN
# ======================
GOAL_KCAL = 1900
GOAL_PROTEIN = 109
GOAL_CARBS = 210
GOAL_FAT = 65

# ======================
# UI
# ======================
st.set_page_config(page_title="Macro Tracker", layout="centered")
st.title("💪 Macro Tracker")

# ======================
# PRODUCT TOEVOEGEN
# ======================
st.subheader("➕ Nieuw product")

name = st.text_input("Naam")
kcal = st.number_input("Kcal", 0)
protein = st.number_input("Eiwit (g)", 0)
carbs = st.number_input("Koolhydraten (g)", 0)
fat = st.number_input("Vet (g)", 0)

if st.button("Opslaan product"):
    db.collection("foods").add({
        "name": name,
        "kcal": kcal,
        "protein": protein,
        "carbs": carbs,
        "fat": fat
    })
    st.success("Opgeslagen")

# ======================
# PRODUCTEN LADEN
# ======================
foods = [f.to_dict() for f in db.collection("foods").stream()]

# ======================
# DAG TOEVOEGEN
# ======================
st.subheader("🍽️ Toevoegen aan dag")

if foods:
    keuze = st.selectbox("Kies product", [f["name"] for f in foods])
    selected = next(f for f in foods if f["name"] == keuze)

    if st.button("Toevoegen"):
        db.collection("log").add({
            "date": str(date.today()),
            **selected
        })
        st.success("Toegevoegd")

# ======================
# DAG OVERZICHT
# ======================
st.subheader("📊 Vandaag")

logs = [
    l.to_dict()
    for l in db.collection("log").stream()
    if l.to_dict()["date"] == str(date.today())
]

if logs:
    total_kcal = sum(x["kcal"] for x in logs)
    total_protein = sum(x["protein"] for x in logs)
    total_carbs = sum(x["carbs"] for x in logs)
    total_fat = sum(x["fat"] for x in logs)

    # metrics
    st.metric("Kcal", f"{total_kcal} / {GOAL_KCAL}")
    st.metric("Eiwit", f"{total_protein} / {GOAL_PROTEIN}")
    st.metric("Carbs", f"{total_carbs} / {GOAL_CARBS}")
    st.metric("Vet", f"{total_fat} / {GOAL_FAT}")

    # remaining
    st.write("### 🔥 Resterend")
    st.write({
        "kcal": GOAL_KCAL - total_kcal,
        "eiwit": GOAL_PROTEIN - total_protein,
        "carbs": GOAL_CARBS - total_carbs,
        "vet": GOAL_FAT - total_fat
    })

    # progress bars
    st.progress(min(total_kcal / GOAL_KCAL, 1.0))
    st.progress(min(total_protein / GOAL_PROTEIN, 1.0))
    st.progress(min(total_carbs / GOAL_CARBS, 1.0))
    st.progress(min(total_fat / GOAL_FAT, 1.0))

else:
    st.write("Nog niks vandaag")
