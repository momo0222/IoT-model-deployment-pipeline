import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("IoT Model Prediction Interface")

st.header("Description")
description = st.text_input("DESCRIPTION", value="This is a DDOS attack.")

st.header("Random Forest Features")
col1, col2 = st.columns(2)

with col1:
    proto = st.text_input("proto", value="tcp")
    service = st.text_input("service", value="-")
    duration = st.number_input("duration", value=290.371539, format="%f")
    src_bytes = st.number_input("src_bytes", value=101568, step=1)
    dst_bytes = st.number_input("dst_bytes", value=2592, step=1)
    conn_state = st.text_input("conn_state", value="OTH")
    missed_bytes = st.number_input("missed_bytes", value=0, step=1)
    src_pkts = st.number_input("src_pkts", value=108, step=1)
    src_ip_bytes = st.number_input("src_ip_bytes", value=108064, step=1)
    dst_pkts = st.number_input("dst_pkts", value=31, step=1)

with col2:
    dst_ip_bytes = st.number_input("dst_ip_bytes", value=3832, step=1)
    dns_qclass = st.number_input("dns_qclass", value=0, step=1)
    dns_qtype = st.number_input("dns_qtype", value=0, step=1)
    dns_rcode = st.number_input("dns_rcode", value=0, step=1)
    dns_AA = st.text_input("dns_AA", value="-")
    dns_RD = st.text_input("dns_RD", value="-")
    dns_RA = st.text_input("dns_RA", value="-")
    dns_rejected = st.text_input("dns_rejected", value="-")
    http_request_body_len = st.number_input("http_request_body_len", value=0, step=1)
    http_response_body_len = st.number_input("http_response_body_len", value=0, step=1)
    http_status_code = st.number_input("http_status_code", value=0, step=1)

rf_inputs = {
    "proto": proto,
    "service": service,
    "duration": duration,
    "src_bytes": src_bytes,
    "dst_bytes": dst_bytes,
    "conn_state": conn_state,
    "missed_bytes": missed_bytes,
    "src_pkts": src_pkts,
    "src_ip_bytes": src_ip_bytes,
    "dst_pkts": dst_pkts,
    "dst_ip_bytes": dst_ip_bytes,
    "dns_qclass": dns_qclass,
    "dns_qtype": dns_qtype,
    "dns_rcode": dns_rcode,
    "dns_AA": dns_AA,
    "dns_RD": dns_RD,
    "dns_RA": dns_RA,
    "dns_rejected": dns_rejected,
    "http_request_body_len": http_request_body_len,
    "http_response_body_len": http_response_body_len,
    "http_status_code": http_status_code,
}

if st.button("Run Prediction"):
    try:
        attack_resp = requests.post(
            f"{API_URL}/predict_attack",
            json={"inputs": {"DESCRIPTION": description}},
            timeout=10,
        )
        severity_resp = requests.post(
            f"{API_URL}/predict_severity",
            json={"inputs": {"DESCRIPTION": description}},
            timeout=10,
        )
        rf_resp = requests.post(
            f"{API_URL}/predict_rf",
            json={"inputs": rf_inputs},
            timeout=10,
        )

        st.subheader("Attack Prediction")
        attack_data = attack_resp.json()
        if attack_data.get("model_loaded"):
            st.write(attack_data.get("prediction"))
        else:
            st.error("Attack model is not loaded.")

        st.subheader("Severity Prediction")
        severity_data = severity_resp.json()
        if severity_data.get("model_loaded"):
            st.write(severity_data.get("prediction"))
        else:
            st.error("Severity model is not loaded.")

    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
