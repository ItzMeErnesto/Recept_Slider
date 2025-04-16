import streamlit as st
import pandas as pd
import joblib
import os

# 📦 Laad model
model_path = os.path.join(os.path.dirname(__file__), "model_rf.pkl")
model = joblib.load(model_path)


st.title("📊 Simulatie: voorspelling Viscositeit, pH en DS")
st.markdown("Gebruik de sliders of typ zelf een getal in. De voorspelling wordt automatisch bijgewerkt.")

st.subheader("🔧 Hoeveelheden grondstoffen (in g of kg)")

def slider_met_input(label, min_val, max_val, default):
    # Eén regel met slider + invoerveld
    col1, col2 = st.columns([3, 1])
    with col1:
        val = st.slider(label, min_value=min_val, max_value=max_val, value=default, step=1.0, key=label + "_slider")
    with col2:
        val = st.number_input(" ", min_value=min_val, max_value=max_val, value=val, step=1.0, key=label + "_input")
    return val

lv_dex    = slider_met_input("LV-Dex (g)",       0.0, 1000.0, 100.0)
hv_dex    = slider_met_input("HV-Dex (g)",       0.0, 1000.0, 50.0)
borax     = slider_met_input("Borax (g)",        0.0, 1000.0, 10.0)
krijt     = slider_met_input("Krijt Slurry (g)", 0.0, 1000.0, 200.0)
mbl       = slider_met_input("MBL (g)",          0.0, 1000.0, 5.0)
la1209    = slider_met_input("LA1209 (g)",       0.0, 1000.0, 5.0)
water     = slider_met_input("Water (g)",        0.0, 2000.0, 500.0)
struktol  = slider_met_input("Struktol (g)",     0.0, 100.0, 5.0)
loog      = slider_met_input("Loog (g)",         0.0, 100.0, 5.0)
suiker    = slider_met_input("Suiker (g)",       0.0, 1000.0, 20.0)

# 🧮 Bereken totaal
totaal = lv_dex + hv_dex + borax + krijt + mbl + la1209 + water + struktol + loog + suiker

if totaal == 0:
    st.error("❌ Totale hoeveelheid is 0 – voeg wat grondstoffen toe.")
else:
    # 📐 Bereken percentages
    PLV_Dex = lv_dex / totaal * 100
    PHV_Dex = hv_dex / totaal * 100
    PBorax = borax / totaal * 100
    PKrijt = krijt / totaal * 100
    PMBL = mbl / totaal * 100
    PLA1209 = la1209 / totaal * 100
    PWater = water / totaal * 100
    PStruktol = struktol / totaal * 100
    PLoog = loog / totaal * 100
    PSuiker = suiker / totaal * 100

    input_data = pd.DataFrame([[
        PLV_Dex, PHV_Dex, PBorax, PKrijt, PMBL,
        PLA1209, PWater, PStruktol, PLoog, PSuiker
    ]], columns=[
        'LV-Dex (%)', 'HV-Dex (%)', 'Borax (%)', 'Krijt Slurry (%)',
        'MBL (%)', 'LA1209 (%)', 'Water (%)', 'Struktol (%)',
        'Loog (%)', 'Suiker (%)'
    ])

    prediction = model.predict(input_data)[0]
    visco, ph, ds = prediction

    st.subheader("📈 Voorspelling")
    col1, col2, col3 = st.columns(3)
    col1.metric("🧪 Viscositeit", f"{visco:.2f} mPa.s")
    col2.metric("🧪 pH", f"{ph:.2f}")
    col3.metric("📦 DS", f"{ds:.2f} %")

    with st.expander("Toon berekende percentages"):
        st.dataframe(input_data.round(2))

# 📘 Zet recept vast met een naam
recept_naam = st.text_input("📋 Geef dit recept een naam", placeholder="Bijv. Recept 2025-04 test")

if st.button("💾 Sla recept op"):
    if totaal == 0:
        st.error("❌ Je kunt geen leeg recept opslaan.")
    elif not recept_naam:
        st.warning("⚠️ Geef eerst een naam aan het recept")
    else:
        schaalfactor = 1000 / totaal
        opgeslagen_recept = {
            "Naam": recept_naam,
            "LV-Dex (kg)": round(lv_dex * schaalfactor, 2),
            "HV-Dex (kg)": round(hv_dex * schaalfactor, 2),
            "Borax (kg)": round(borax * schaalfactor, 2),
            "Krijt Slurry (kg)": round(krijt * schaalfactor, 2),
            "MBL (kg)": round(mbl * schaalfactor, 2),
            "LA1209 (kg)": round(la1209 * schaalfactor, 2),
            "Water (kg)": round(water * schaalfactor, 2),
            "Struktol (kg)": round(struktol * schaalfactor, 2),
            "Loog (kg)": round(loog * schaalfactor, 2),
            "Suiker (kg)": round(suiker * schaalfactor, 2),
            "Viscositeit": round(visco, 2),
            "pH": round(ph, 2),
            "DS": round(ds, 2)
        }

        if "opgeslagen_recepten" not in st.session_state:
            st.session_state.opgeslagen_recepten = []

        st.session_state.opgeslagen_recepten.append(opgeslagen_recept)
        st.success(f"✅ Recept '{recept_naam}' opgeslagen (omgerekend naar 1000 kg)")

# 📊 Toon opgeslagen recepten
if "opgeslagen_recepten" in st.session_state and st.session_state.opgeslagen_recepten:
    st.subheader("📘 Opgeslagen recepten (1000 kg totaal)")

    df_opgeslagen = pd.DataFrame(st.session_state.opgeslagen_recepten)

    # 🔍 Zoek/filter op naam of ingrediënt
    zoekterm = st.text_input("🔎 Zoek op naam of grondstof")
    if zoekterm:
        df_opgeslagen = df_opgeslagen[df_opgeslagen.apply(lambda row: zoekterm.lower() in row.astype(str).str.lower().to_string(), axis=1)]

    # 📌 Recept-vergelijking
    st.markdown("### 📊 Vergelijk recepten")
    geselecteerde_namen = st.multiselect("Selecteer recepten om te vergelijken", df_opgeslagen["Naam"].unique())
    if geselecteerde_namen:
        st.dataframe(df_opgeslagen[df_opgeslagen["Naam"].isin(geselecteerde_namen)].set_index("Naam"))

    # ❌ Verwijder individuele rijen
    st.markdown("### ❌ Verwijder individuele recepten")
    for i, row in df_opgeslagen.iterrows():
        cols = st.columns([10, 1])
        cols[0].write(row.to_frame().T)
        if cols[1].button("❌", key=f"delete_{i}"):
            st.session_state.opgeslagen_recepten.pop(i)
            st.experimental_rerun()

    # 📥 Download naar Excel
    export_df = pd.DataFrame(st.session_state.opgeslagen_recepten)
    from io import BytesIO

    # Exporteer naar geheugen (i.p.v. direct bestand)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Recepten')
    output.seek(0)

    st.download_button(
        label="📥 Exporteer naar Excel",
        data=output,
        file_name="opgeslagen_recepten.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🧹 Reset alles"):
        st.session_state.opgeslagen_recepten = []
        st.success("🧼 Alles is gereset!")
        st.stop()  # stopt verdere verwerking — veilig alternatief

