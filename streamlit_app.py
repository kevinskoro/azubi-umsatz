import streamlit as st
import pandas as pd
from datetime import date

# Datei zum Speichern
DATA_FILE = "umsatzdaten.csv"

# Setzt den Titel
st.title("💼 Merch-Umsatz-Dashboard")

# Lege deine Azubis und Statusstufen fest
azubis = {
    "Cemo": ["Merch", "Junior Trainer", "Senior Trainer", "Assistenz Manager", "Junior Sales Partner", "Sales Partner"],
    "Immanuel": ["Merch", "Junior Trainer", "Senior Trainer", "Assistenz Manager", "Junior Sales Partner", "Sales Partner"]
}

# Lese Daten aus Datei
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Datum", "Azubi", "Umsatz (€)", "Status"])

# Speichere neue Daten
def save_data(new_entry):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# ADMIN-Eingabe
with st.expander("🛠️ Umsatz eintragen (nur du siehst das)"):
    with st.form("umsatz_form"):
        datum = st.date_input("Datum", value=date.today())
        azubi = st.selectbox("Azubi", list(azubis.keys()))
        umsatz = st.number_input("Umsatz in €", min_value=0.0, step=10.0)
        status = st.selectbox("Status", azubis[azubi])
        submitted = st.form_submit_button("Speichern")

        if submitted:
            new_data = {
                "Datum": datum.strftime("%Y-%m-%d"),
                "Azubi": azubi,
                "Umsatz (€)": umsatz,
                "Status": status
            }
            save_data(new_data)
            st.success("✅ Umsatz gespeichert!")

# Anzeige aller Daten
st.subheader("📊 Umsatzübersicht")
data = load_data()

if data.empty:
    st.info("Noch keine Umsätze eingetragen.")
else:
    # Optional sortieren
    data["Datum"] = pd.to_datetime(data["Datum"])
    data = data.sort_values(by="Datum", ascending=False)
    st.dataframe(data, use_container_width=True)

    # Summe pro Azubi
    st.subheader("📈 Gesamtumsätze")
    summary = data.groupby("Azubi")["Umsatz (€)"].sum().reset_index()
    st.table(summary)
