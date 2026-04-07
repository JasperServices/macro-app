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

st.set_page_config(page_title="Macro Tracker", layout="centered")
st.title("💪 Macro Tracker (stabiel + per 100g)")

# ======================
# PRODUCT TOEVOEGEN
# ======================
st.subheader("➕ Nieuw product (per 100g)")

with st.form("product_form"):
    name = st.text_input("Naam")
    kcal = st.number_input("Kcal per 100g", min_value=0)
    protein = st.number_input("Eiwit per 100g", min_value=0)
    carbs = st.number_input("Koolhydraten per 100g", min_value=0)
    fat = st.number_input("Vet per 100g", min_value=0)

    submit_product = st.form_submit_button("Opslaan product")

    if submit_product and name:
        db.collection("foods").add({
            "name": name,
            "kcal": kcal,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        })
        st.success("Product opgeslagen")
        st.rerun()

# ======================
# PRODUCTEN LADEN
# ======================
foods_ref = db.collection("foods").stream()
foods = [f.to_dict() for f in foods_ref]
names = [f["name"] for f in foods]

# ======================
# ETEN TOEVOEGEN
# ======================
st.subheader("🍽️ Eten toevoegen")

with st.form("log_form"):
    if foods:
        keuze = st.selectbox("Kies product", names)
        grams = st.number_input("Hoeveel gram gegeten?", min_value=0)

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

# ======================
# DAG DATA
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

    st.metric("Kcal", f"{int(total_kcal)} / {GOAL_KCAL}")
    st.metric("Eiwit", f"{int(total_protein)} / {GOAL_PROTEIN}")
    st.metric("Carbs", f"{int(total_carbs)} / {GOAL_CARBS}")
    st.metric("Vet", f"{int(total_fat)} / {GOAL_FAT}")

    st.write("### 🔥 Progress")

    st.progress(min(total_kcal / GOAL_KCAL, 1.0))
    st.progress(min(total_protein / GOAL_PROTEIN, 1.0))
    st.progress(min(total_carbs / GOAL_CARBS, 1.0))
    st.progress(min(total_fat / GOAL_FAT, 1.0))

else:
    st.write("Nog niks vandaag")
