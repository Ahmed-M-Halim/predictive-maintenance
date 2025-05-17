import streamlit as st
import pandas as pd
import numpy as np
import pickle
import altair as alt
import os

# Load the model
with open('dt.pkl', 'rb') as file:
    model = pickle.load(file)

st.set_page_config(page_title="Equipment Failure Prediction", layout="wide")
st.title("Equipment Failure Prediction Dashboard")
st.markdown("A smart application to predict equipment failure based on oil and metal properties.")

# General Info
st.markdown("## General Info")
col1, col2 = st.columns(2)
with col1:
    Meter_Hr = st.number_input("Meter Hour", min_value=157.4, max_value=462.0, value=200.0)
    Fluid_Brand = st.number_input("Fluid Brand", min_value=0, max_value=3, value=0)
    Fluid_Type = st.number_input("Fluid Type", min_value=0, max_value=3, value=0)
    Fluid_Weight = st.number_input("Fluid Weight", min_value=0, max_value=3, value=0)
    Filter_Change = st.selectbox("Filter Changed?", [0, 1])
    Fluid_Change = st.selectbox("Fluid Changed?", [0, 1])
with col2:
    Compressor_Meter_Hr = st.number_input("Compressor Meter Hour", min_value=134.8, max_value=379.3, value=200.0)
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

# Prepare input data
input_data = pd.DataFrame([[
    Meter_Hr, Fluid_Brand, Fluid_Type, Fluid_Weight, Filter_Change, Fluid_Change,
    Compressor_Meter_Hr, Cu, Fe, Cr, Al, Si, Pb, Sn, Ni, Na, B, Zn, Mo, Ca, Mg, P,
    Water_Present, Antifreeze_Present, TBN, TAN, OXI, V100, V40
]], columns=[
    'Meter_Hr', 'Fluid_Brand', 'Fluid_Type', 'Fluid_Weight', 'Filter_Change', 'Fluid_Change',
    'Compressor_Meter_Hr', 'Cu', 'Fe', 'Cr', 'Al', 'Si', 'Pb', 'Sn', 'Ni', 'Na', 'B', 'Zn',
    'Mo', 'Ca', 'Mg', 'P', 'Water_Present', 'Antifreeze_Present', 'TBN', 'TAN', 'OXI', 'V100', 'V40'
])

# Prediction
if st.button("Predict Failure", key="predict_btn"):
    prediction = model.predict(input_data)
    label = "⚠️ Failure Expected" if prediction[0] == 1 else "✅ No Failure"
    st.success(f"Prediction: {label}")

    # Wear Metals Dashboard
    st.markdown("## Wear Metals Dashboard")
    st.markdown("### Input values vs. Normal value (1.0)")

    wear_metals = {
        "Cu (Copper)": Cu,
        "Fe (Iron)": Fe,
        "Pb (Lead)": Pb
    }

    col1, col2, col3 = st.columns(3)

    for i, (metal, value) in enumerate(wear_metals.items()):
        df = pd.DataFrame({
            "Type": ["Entered", "Normal"],
            "Value": [value, 1.0]
        })

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Type', title=''),
            y=alt.Y('Value', title='Value'),
            color=alt.Color('Type', scale=alt.Scale(
                domain=["Entered", "Normal"],
                range=["#FF6961", "#77DD77"]
            )),
            tooltip=['Type', 'Value']
        ).properties(
            width=150,
            height=250,
            title=metal
        )

        if i == 0:
            col1.altair_chart(chart, use_container_width=True)
        elif i == 1:
            col2.altair_chart(chart, use_container_width=True)
        else:
            col3.altair_chart(chart, use_container_width=True)

# Create a DataFrame with both input and prediction
output_df = input_data.copy()
output_df["prediction"] = prediction

# Save to CSV (overwrite or append based on your logic)
csv_path = "prediction_result.csv"

# You can choose to overwrite or append
if os.path.exists(csv_path):
    output_df.to_csv(csv_path, mode='a', index=False, header=False)
else:
    output_df.to_csv(csv_path, index=False)
