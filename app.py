import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date

# firebase verbinden
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("🍽️ Macro Tracker")

# --- nieuw product ---
st.subheader("Nieuw product")
name = st.text_input("Naam")
kcal = st.number_input("Kcal", 0)
protein = st.number_input("Eiwit", 0)
carbs = st.number_input("Koolhydraten", 0)
fat = st.number_input("Vet", 0)

if st.button("Opslaan"):
    db.collection("foods").add({
        "name": name,
        "kcal": kcal,
        "protein": protein,
        "carbs": carbs,
        "fat": fat
    })
    st.success("Opgeslagen")

# --- producten ophalen ---
foods = [f.to_dict() for f in db.collection("foods").stream()]

# --- kiezen ---
st.subheader("Voeg toe")
if foods:
    keuze = st.selectbox("Kies product", [f["name"] for f in foods])
    selected = next(f for f in foods if f["name"] == keuze)

    if st.button("Toevoegen aan dag"):
        db.collection("log").add({
            "date": str(date.today()),
            **selected
        })
        st.success("Toegevoegd")

# --- dag totaal ---
st.subheader("Vandaag")
logs = [l.to_dict() for l in db.collection("log").stream()
        if l.to_dict()["date"] == str(date.today())]

if logs:
    st.write("Totaal kcal:", sum(x["kcal"] for x in logs))
else:
    st.write("Nog niks")
