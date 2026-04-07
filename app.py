import streamlit as st

# ======================
# STREAMLIT CONFIG (MOET EERST)
# ======================
st.set_page_config(page_title="Macro Tracker", layout="centered")
st.title("💪 Macro Tracker")

# ======================
# IMPORTS
# ======================
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
# DATA LOAD (simpel, stabiel)
# ======================
def load_foods():
    return [f.to_dict() for f in db.collection("foods").stream()]

def load_logs():
    return [l.to_dict() for l in db.collection("log").stream()]

# ======================
# DATA
# ======================
foods = load_foods()
names = [f["name"] for f in foods] if foods else []

# ======================
# OVERZICHT
# ======================
st.subheader("📊 Vandaag")

logs = load_logs()
today = str(date.today())
today_logs = [l for l in logs if l["date"] == today]

if today_logs:
    kcal = sum(x["kcal"] for x in today_logs)
    protein = sum(x["protein"] for x in today_logs)
    carbs = sum(x["carbs"] for x in today_logs)
    fat = sum(x["fat"] for x in today_logs)

    st.metric("Kcal", f"{int(kcal)} / {GOAL_KCAL}")
    st.metric("Eiwit", f"{int(protein)} / {GOAL_PROTEIN}")
    st.metric("Carbs", f"{int(carbs)} / {GOAL_CARBS}")
    st.metric("Vet", f"{int(fat)} / {GOAL_FAT}")

    st.progress(min(kcal / GOAL_KCAL, 1.0))
    st.progress(min(protein / GOAL_PROTEIN, 1.0))
    st.progress(min(carbs / GOAL_CARBS, 1.0))
    st.progress(min(fat / GOAL_FAT, 1.0))
else:
    st.info("Nog niks vandaag")

st.divider()

# ======================
# PRODUCT TOEVOEGEN
# ======================
st.subheader("➕ Product (per 100g)")

with st.form("product_form"):
    name = st.text_input("Naam")
    kcal = st.number_input("Kcal per 100g", min_value=0)
    protein = st.number_input("Eiwit per 100g", min_value=0)
    carbs = st.number_input("Carbs per 100g", min_value=0)
    fat = st.number_input("Vet per 100g", min_value=0)

    submit = st.form_submit_button("Opslaan")

    if submit and name.strip():
        db.collection("foods").add({
            "name": name,
            "kcal": kcal,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        })

        st.success("Product opgeslagen")
        st.rerun()

st.divider()

# ======================
# ETEN LOGGEN
# ======================
st.subheader("🍽️ Eten toevoegen")

foods = load_foods()
names = [f["name"] for f in foods] if foods else []

if names:
    with st.form("log_form"):
        keuze = st.selectbox("Product", names)
        grams = st.number_input("Gram gegeten", min_value=0)

        submit_log = st.form_submit_button("Toevoegen")

        if submit_log:
            selected = next(f for f in foods if f["name"] == keuze)
            factor = grams / 100

            db.collection("log").add({
                "date": str(date.today()),
                "name": selected["name"],
                "kcal": selected["kcal"] * factor,
                "protein": selected["protein"] * factor,
                "carbs": selected["carbs"] * factor,
                "fat": selected["fat"] * factor
            })

            st.success("Toegevoegd")
            st.rerun()
