import streamlit as st

# Title of the app
st.title("Simple BMI Calculator")

# Input fields that turn into mobile-friendly sliders
weight = st.slider("Select your Weight (kg)", 40, 150, 70)
height_cm = st.slider("Select your Height (cm)", 100, 220, 170)

# Convert height to meters for the formula
height_m = height_cm / 100

# Calculate BMI
if st.button("Calculate"):
    bmi = weight / (height_m ** 2)
    st.success(f"Your BMI is {bmi:.1f}")
    
    # Provide context
    if bmi < 18.5:
        st.warning("Underweight")
    elif 18.5 <= bmi < 25:
        st.info("Normal weight")
    else:
        st.error("Overweight")
