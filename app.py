import streamlit as st
import pandas as pd
import pickle
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from Reasoning import Reasoning_Model  

# --- Page config ---
st.set_page_config(page_title="Equipment Failure Prediction", layout="wide")
st.title("🔍 Equipment Failure Prediction Dashboard")
st.markdown("This app predicts equipment failure class using either manual inputs or image-based oil analysis.")

# --- Reset button ---
if st.button("🔁 Reset Inputs"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# --- Load model ---
with open('dt.pkl', 'rb') as file:
    model = pickle.load(file)

# --- Load Reasoning Model ---
@st.cache_resource
def load_reasoning_model():
    return Reasoning_Model()

reasoning_model = load_reasoning_model()

# --- Input Columns ---
input_columns = [
    'Cu', 'Fe', 'Cr', 'Al', 'Si', 'Pb', 'Sn', 'Ni', 'Na', 'B',
    'P', 'Zn', 'Mo', 'Ca', 'Mg', 'TBN', 'V100', 'V40',
    'OXI', 'TAN', 'delta_visc_40', 'metal_sum',
    'iron_to_copper_ratio', 'water_flag', 'antifreeze_flag'
]

# --- Input Mode Selection ---
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "📝 Manual Entry"
input_mode = st.radio("Choose Input Mode", ["📝 Manual Entry", "📷 Upload Image"],
                      index=["📝 Manual Entry", "📷 Upload Image"].index(st.session_state.input_mode),
                      horizontal=True)
st.session_state.input_mode = input_mode

# --- Input Data Placeholder ---
if "input_data" not in st.session_state:
    st.session_state.input_data = None

# --- Manual Entry ---
if input_mode == "📝 Manual Entry":
    with st.form("manual_form"):
        st.markdown("### 🛠 Enter Oil Analysis Features")
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
        submit_manual = st.form_submit_button("🔍 Predict")

        if submit_manual:
            st.session_state.input_data = pd.DataFrame([[Cu, Fe, Cr, Al, Si, Pb, Sn, Ni, Na, B, P, Zn, Mo, Ca, Mg,
                                                         TBN, V100, V40, OXI, TAN, delta_visc_40, metal_sum,
                                                         iron_to_copper_ratio, water_flag, antifreeze_flag]],
                                                       columns=input_columns)

# --- Upload Image Mode (To be added later) ---
elif input_mode == "📷 Upload Image":
    st.info("📷 Image mode will be supported soon. Stay tuned!")

# --- Prediction Section ---
if st.session_state.input_data is not None:
    input_data = st.session_state.input_data
    prediction = model.predict(input_data)[0]
    st.success(f"🔧 Predicted Failure Class: *{prediction}*")

    # Save to Google Sheets
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        sheet = gspread.authorize(creds).open("Equipment_Predictions").sheet1
        row = list(input_data.iloc[0].values) + [prediction]
        sheet.append_row(row)
        st.info("✅ Saved to Google Sheet.")
    except Exception as e:
        st.warning(f"⚠ Could not save to Google Sheet: {e}")

    # 📊 Visual Placeholder
    st.markdown("### 📊 Data Visualization")
    st.write("✅ Add your plots here...")

    # 🧠 LLM Reasoning
    try:
        sample_str = ', '.join([f"{col}: {val}" for col, val in zip(input_columns, input_data.iloc[0].values)])
        reasoning_text = reasoning_model.generate_response(prediction, sample_str)
        st.markdown("### 💬 LLM Reasoning")
        st.info(reasoning_text)
    except Exception as e:
        st.warning(f"⚠ Could not generate reasoning: {e}")

    # 🔊 Audio Explanation
    if st.button("🎧 Listen to Reasoning"):
        try:
            audio_api_url = f"https://example.com/api/get_audio?text={reasoning_text}"
            response = requests.get(audio_api_url)
            if response.status_code == 200:
                st.audio(response.content, format="audio/mp3")
            else:
                st.warning("⚠ Could not fetch the audio.")
        except Exception as e:
            st.error(f"❌ Audio Error: {e}")
