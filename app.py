import streamlit as st
import pandas as pd
import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load the trained model
with open('dt.pkl', 'rb') as file:
    model = pickle.load(file)

st.set_page_config(page_title="Equipment Failure Prediction", layout="wide")
st.title("Equipment Failure Prediction Dashboard")

st.markdown("This app predicts the failure class of equipment based on oil analysis.")

# Define input columns matching Google Sheet order
input_columns = [
    'Cu', 'Fe', 'Cr', 'Al', 'Si', 'Pb', 'Sn', 'Ni', 'Na', 'B',
    'P', 'Zn', 'Mo', 'Ca', 'Mg', 'TBN', 'V100', 'V40',
    'OXI', 'TAN', 'delta_visc_40', 'metal_sum',
    'iron_to_copper_ratio', 'water_flag', 'antifreeze_flag'
]

# Create Streamlit inputs
st.markdown("### Enter Oil Analysis Features")

col1, col2 = st.columns(2)
with col1:
    Cu = st.number_input("Cu", 0.0, 100.0, 5.0)
    Fe = st.number_input("Fe", 0.0, 100.0, 6.0)
    Cr = st.number_input("Cr", 0.0, 100.0, 0.0)
    Al = st.number_input("Al", 0.0, 100.0, 1.0)
    Si = st.number_input("Si", 0.0, 100.0, 3.0)
    Pb = st.number_input("Pb", 0.0, 100.0, 18.0)
    Sn = st.number_input("Sn", 0.0, 100.0, 1.0)
    Ni = st.number_input("Ni", 0.0, 100.0, 0.0)
    Na = st.number_input("Na", 0.0, 100.0, 8.0)
    B = st.number_input("B", 0.0, 100.0, 1.0)
    P = st.number_input("P", 0.0, 100.0, 15.0)
    Zn = st.number_input("Zn", 0.0, 100.0, 15.0)
with col2:
    Mo = st.number_input("Mo", 0.0, 100.0, 0.0)
    Ca = st.number_input("Ca", 0.0, 500.0, 256.0)
    Mg = st.number_input("Mg", 0.0, 100.0, 0.0)
    TBN = st.number_input("TBN", 0.0, 10.0, 8.5)
    V100 = st.number_input("V100", 0.0, 100.0, 10.0)
    V40 = st.number_input("V40", 0.0, 200.0, 150.0)
    OXI = st.number_input("OXI", 0.0, 100.0, 0.0)
    TAN = st.number_input("TAN", 0.0, 2.0, 0.04)
    delta_visc_40 = st.number_input("Delta Viscosity 40", -100.0, 100.0, 0.0)
    metal_sum = st.number_input("Metal Sum", 0.0, 1000.0, 50.0)
    iron_to_copper_ratio = st.number_input("Fe to Cu Ratio", 0.0, 100.0, 1.0)
    water_flag = st.selectbox("Water Present?", [0, 1])
    antifreeze_flag = st.selectbox("Antifreeze Present?", [0, 1])

# Prepare input in correct order
input_data = pd.DataFrame([[
    Cu, Fe, Cr, Al, Si, Pb, Sn, Ni, Na, B,
    P, Zn, Mo, Ca, Mg, TBN, V100, V40,
    OXI, TAN, delta_visc_40, metal_sum,
    iron_to_copper_ratio, water_flag, antifreeze_flag
]], columns=input_columns)

# Predict
if st.button("Predict Failure"):
    prediction = model.predict(input_data)[0]
    st.success(f"Predicted Failure Class: 🔧 {prediction}")

    # Save to Google Sheet
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

    # Optional Power BI link
    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiMDI3YzcyNDktMTJkOS00MTU2LTlmZmUtNzExMmQ3MTg2NTU3IiwidCI6Ijg1OTQ4YjFkLTZhOGQtNGIxNy1hMjVhLTliNjA0YmY2NDI2OCIsImMiOjh9"
    st.markdown(f"[🔗 View Power BI Dashboard]({powerbi_url})", unsafe_allow_html=True)
