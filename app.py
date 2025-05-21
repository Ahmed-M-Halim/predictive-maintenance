import streamlit as st
import pandas as pd
import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load model
with open('dt.pkl', 'rb') as file:
    model = pickle.load(file)

st.set_page_config(page_title="Equipment Failure Prediction", layout="wide")
st.title("Equipment Failure Prediction Dashboard")

st.markdown("This app predicts the failure class of equipment based on oil analysis features.")

# Define all input columns based on cleaned_synthetic_oil_data.csv
input_columns = [
    'Cu', 'Fe', 'Cr', 'Al', 'Si', 'Pb', 'Sn', 'Ni', 'Na', 'B',
    'Zn', 'Mo', 'Ca', 'Mg', 'P', 'TBN', 'TAN', 'OXI', 'V100', 'V40',
    'Water_Present', 'Antifreeze_Present', 'Filter_Change', 'Fluid_Change',
    'metal_sum', 'delta_visc', 'wear_ratio'
]

# Split into sections
st.markdown("### Wear Metals")
metals_cols = input_columns[:10]
col1, col2 = st.columns(2)
with col1:
    Cu = st.number_input("Cu", 0.0, 100.0, 5.0)
    Fe = st.number_input("Fe", 0.0, 100.0, 6.0)
    Cr = st.number_input("Cr", 0.0, 100.0, 0.0)
    Al = st.number_input("Al", 0.0, 100.0, 1.0)
    Si = st.number_input("Si", 0.0, 100.0, 3.0)
with col2:
    Pb = st.number_input("Pb", 0.0, 100.0, 18.0)
    Sn = st.number_input("Sn", 0.0, 100.0, 1.0)
    Ni = st.number_input("Ni", 0.0, 100.0, 0.0)
    Na = st.number_input("Na", 0.0, 100.0, 8.0)
    B = st.number_input("B", 0.0, 100.0, 1.0)

st.markdown("### Additives & Chemical Properties")
col1, col2 = st.columns(2)
with col1:
    Zn = st.number_input("Zn", 0.0, 100.0, 15.0)
    Mo = st.number_input("Mo", 0.0, 100.0, 0.0)
    Ca = st.number_input("Ca", 0.0, 500.0, 256.0)
    Mg = st.number_input("Mg", 0.0, 100.0, 0.0)
    P = st.number_input("P", 0.0, 100.0, 15.0)
with col2:
    TBN = st.number_input("TBN", 0.0, 10.0, 8.5)
    TAN = st.number_input("TAN", 0.0, 2.0, 0.04)
    OXI = st.number_input("OXI", 0.0, 100.0, 0.0)
    V100 = st.number_input("V100", 0.0, 100.0, 10.0)
    V40 = st.number_input("V40", 0.0, 200.0, 150.0)

st.markdown("### Operational Flags & Ratios")
col1, col2 = st.columns(2)
with col1:
    Water_Present = st.selectbox("Water Present?", [0, 1])
    Antifreeze_Present = st.selectbox("Antifreeze Present?", [0, 1])
with col2:
    Filter_Change = st.selectbox("Filter Changed?", [0, 1])
    Fluid_Change = st.selectbox("Fluid Changed?", [0, 1])

col1, col2 = st.columns(2)
with col1:
    metal_sum = st.number_input("Metal Sum", 0.0, 1000.0, 50.0)
    delta_visc = st.number_input("Delta Viscosity", -100.0, 100.0, 0.0)
with col2:
    wear_ratio = st.number_input("Wear Ratio", 0.0, 100.0, 1.0)

# Collect all input values into a single row
input_data = pd.DataFrame([[
    Cu, Fe, Cr, Al, Si, Pb, Sn, Ni, Na, B,
    Zn, Mo, Ca, Mg, P, TBN, TAN, OXI, V100, V40,
    Water_Present, Antifreeze_Present, Filter_Change, Fluid_Change,
    metal_sum, delta_visc, wear_ratio
]], columns=input_columns)

# Predict button
if st.button("Predict Failure"):
    prediction = model.predict(input_data)[0]
    st.success(f"Predicted Failure Class: 🛠️ {prediction}")

    # Save to Google Sheets
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Equipment_Predictions").sheet1
        row = list(input_data.iloc[0].values) + [prediction]
        sheet.append_row(row)
        st.info("✅ Prediction saved to Google Sheet.")
    except Exception as e:
        st.error(f"❌ Failed to save to Google Sheet: {e}")

    # Power BI link
    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiMDI3YzcyNDktMTJkOS00MTU2LTlmZmUtNzExMmQ3MTg2NTU3IiwidCI6Ijg1OTQ4YjFkLTZhOGQtNGIxNy1hMjVhLTliNjA0YmY2NDI2OCIsImMiOjh9"
    st.markdown(f"[🔗 View Power BI Dashboard]({powerbi_url})", unsafe_allow_html=True)
