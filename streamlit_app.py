import streamlit as st
import pandas as pd
from datetime import date
import altair as alt

DATA_FILE = "umsatzdaten.csv"
st.set_page_config(page_title="Azubi-Umsatz", layout="wide")
st.title("💼 Azubi-Umsatz-Dashboard")

azubis = {
    "Cemo": ["Merch", "Junior Trainer", "Senior Trainer", "Assistenz Manager", "Junior Sales Partner", "Sales Partner"],
    "Immanuel": ["Merch", "Junior Trainer", "Senior Trainer", "Assistenz Manager", "Junior Sales Partner", "Sales Partner"]
}

# Laden & Speichern mit Fehlerbehandlung beim Datum
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
        # Datum in datetime, Fehler werden zu NaT konvertiert
        df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
        # Zeilen mit ungültigem Datum entfernen
        df = df.dropna(subset=["Datum"])
        df["KW"] = df["Datum"].dt.isocalendar().week
        df["Monat"] = df["Datum"].dt.month
        df["Jahr"] = df["Datum"].dt.year
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Datum", "Azubi", "Umsatz (€)", "Status", "KW", "Monat", "Jahr"])

def save_data(new_entry):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Eingabeformular
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

# Daten laden
df = load_data()

if df.empty:
    st.info("Noch keine Umsätze eingetragen.")
    st.stop()

# Filter: Jahr, Monat, Woche
st.subheader("📅 Filter")

col1, col2, col3 = st.columns(3)
with col1:
    jahr = st.selectbox("Jahr", sorted(df["Jahr"].unique()), index=len(df["Jahr"].unique())-1)
with col2:
    monat = st.selectbox("Monat (optional)", ["Alle"] + sorted(df["Monat"].unique().tolist()))
with col3:
    kw = st.selectbox("Kalenderwoche (optional)", ["Alle"] + sorted(df["KW"].unique().tolist()))

# Filter anwenden
df = df[df["Jahr"] == jahr]
if monat != "Alle":
    df = df[df["Monat"] == monat]
if kw != "Alle":
    df = df[df["KW"] == kw]

# Umsatzübersicht Tabelle
st.subheader("📊 Umsatzübersicht")
df_sorted = df.sort_values(by="Datum", ascending=False)
st.dataframe(df_sorted[["Datum", "Azubi", "Umsatz (€)", "Status"]], use_container_width=True)

# Gesamtumsätze
st.subheader("📈 Gesamtumsätze")
summary = df.groupby("Azubi")["Umsatz (€)"].sum().round(2).reset_index()
st.table(summary)

# Diagramme pro Azubi
st.subheader("📉 Umsatz nach Kalenderwochen (Standardansicht)")
for azubi in df["Azubi"].unique():
    st.markdown(f"### 👤 {azubi}")
    azubi_df = df[df["Azubi"] == azubi]
    if azubi_df.empty:
        st.info("Keine Daten für diesen Azubi.")
        continue
    grouped = azubi_df.groupby(["KW"])["Umsatz (€)"].sum().reset_index()

    chart = alt.Chart(grouped).mark_bar(color="#4B8BBE").encode(
        x=alt.X("KW:O", title="Kalenderwoche"),
        y=alt.Y("Umsatz (€):Q", title="Gesamtumsatz (€)"),
        tooltip=["KW", "Umsatz (€)"]
    ).properties(width=700, height=300)

    st.altair_chart(chart, use_container_width=True)
