import json
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Model Prediction Interface")
st.write("Enter input JSON for the model")

raw_input = st.text_area(
    "Input",
    value = '{\n "feature_1": 10, \n "feature_2": "example" \n}',
    height=160
)

if st.button("Run Prediction"):
    try: 
        parsed_input = json.loads(raw_input)
        payload = {"inputs": parsed_input}

        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        st.json(response.json())
    
    except json.JSONDecodeError:
        st.error("Invalid JSON format! Please check your syntax")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")