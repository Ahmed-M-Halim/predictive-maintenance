import streamlit as st
import pandas as pd
import pickle
import altair as alt
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Load model
with open('dt.pkl', 'rb') as file:
    model = pickle.load(file)

st.set_page_config(page_title="Equipment Failure Prediction", layout="wide")
st.title("Equipment Failure Prediction Dashboard")
st.markdown("This app predicts equipment failure based on oil and metal properties.")

# General Info
st.markdown("## General Info")
col1, col2 = st.columns(2)
with col1:
    Meter_Hr = st.number_input("Meter Hour", 157.4, 462.0, 200.0)
    Fluid_Brand = st.number_input("Fluid Brand", 0, 3, 0)
    Fluid_Type = st.number_input("Fluid Type", 0, 3, 0)
    Fluid_Weight = st.number_input("Fluid Weight", 0, 3, 0)
    Filter_Change = st.selectbox("Filter Changed?", [0, 1])
    Fluid_Change = st.selectbox("Fluid Changed?", [0, 1])
with col2:
    Compressor_Meter_Hr = st.number_input("Compressor Meter Hour", 134.8, 379.3, 200.0)
    Water_Present = st.selectbox("Water Present?", [0, 1])
    Antifreeze_Present = st.selectbox("Antifreeze Present?", [0, 1])

# Wear Metals
st.markdown("## Wear Metals")
col1, col2 = st.columns(2)
with col1:
    Cu = st.number_input("Cu", 0.0, 6.62)
    Fe = st.number_input("Fe", 0.0, 11.77)
    Cr = st.number_input("Cr", 0.0, 3.89)
    Al = st.number_input("Al", 0.0, 3.89)
    Si = st.number_input("Si", 0.0, 3.74)
with col2:
    Pb = st.number_input("Pb", 0.0, 3.68)
    Sn = st.number_input("Sn", 0.0, 3.78)
    Ni = st.number_input("Ni", 0.0, 3.71)
    Na = st.number_input("Na", 0.0, 3.81)
    B = st.number_input("B", 0.0, 2.41)

# Additives & Properties
st.markdown("## Additives & Properties")
col1, col2 = st.columns(2)
with col1:
    Zn = st.number_input("Zn", 4.35, 35.82)
    Mo = st.number_input("Mo", 0.0, 2.41)
    Ca = st.number_input("Ca", 18.66, 35.26)
    Mg = st.number_input("Mg", 0.0, 3.13)
    P = st.number_input("P", 11.0, 20.67)
with col2:
    TBN = st.number_input("TBN", 0.46, 7.30)
    TAN = st.number_input("TAN", 0.0, 1.76)
    OXI = st.number_input("OXI", 0.0, 7.11)
    V100 = st.number_input("V100", 6.64, 13.17)
    V40 = st.number_input("V40", 44.24, 82.77)

# Prepare input
input_data = pd.DataFrame([[
    Meter_Hr, Fluid_Brand, Fluid_Type, Fluid_Weight, Filter_Change, Fluid_Change,
    Compressor_Meter_Hr, Cu, Fe, Cr, Al, Si, Pb, Sn, Ni, Na, B, Zn, Mo, Ca, Mg, P,
    Water_Present, Antifreeze_Present, TBN, TAN, OXI, V100, V40
]], columns=[
    'Meter_Hr', 'Fluid_Brand', 'Fluid_Type', 'Fluid_Weight', 'Filter_Change', 'Fluid_Change',
    'Compressor_Meter_Hr', 'Cu', 'Fe', 'Cr', 'Al', 'Si', 'Pb', 'Sn', 'Ni', 'Na', 'B', 'Zn',
    'Mo', 'Ca', 'Mg', 'P', 'Water_Present', 'Antifreeze_Present', 'TBN', 'TAN', 'OXI', 'V100', 'V40'
])

# Predict button
if st.button("Predict Failure"):
    prediction = model.predict(input_data)
    label = "⚠️ Failure Expected" if prediction[0] == 1 else "✅ No Failure"
    st.success(f"Prediction: {label}")

    # Dashboard
    st.markdown("## Wear Metals Dashboard")
    st.markdown("### Input values vs. Normal value (1.0)")
    wear_metals = {"Cu": Cu, "Fe": Fe, "Pb": Pb}
    col1, col2, col3 = st.columns(3)
    for i, (metal, value) in enumerate(wear_metals.items()):
        df = pd.DataFrame({"Type": ["Entered", "Normal"], "Value": [value, 1.0]})
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Type', title=''),
            y=alt.Y('Value', title='Value'),
            color=alt.Color('Type', scale=alt.Scale(domain=["Entered", "Normal"], range=["#FF6961", "#77DD77"])),
            tooltip=['Type', 'Value']
        ).properties(width=150, height=250, title=metal)
        if i == 0:
            col1.altair_chart(chart, use_container_width=True)
        elif i == 1:
            col2.altair_chart(chart, use_container_width=True)
        else:
            col3.altair_chart(chart, use_container_width=True)

    # Save to Google Sheets
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        import json
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Equipment_Predictions").sheet1
        row = list(input_data.iloc[0].values) + [int(prediction[0])]
        sheet.append_row(row)
        st.info("Prediction saved to Google Sheet ✅")
    except Exception as e:
        st.error(f"Failed to save to Google Sheet: {e}")

    # Link to Power BI report
    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiMDI3YzcyNDktMTJkOS00MTU2LTlmZmUtNzExMmQ3MTg2NTU3IiwidCI6Ijg1OTQ4YjFkLTZhOGQtNGIxNy1hMjVhLTliNjA0YmY2NDI2OCIsImMiOjh9"  # ⬅️ Replace with your actual URL
    st.markdown(f"[🔗 View Dashboard in Power BI Online]({powerbi_url})", unsafe_allow_html=True)
