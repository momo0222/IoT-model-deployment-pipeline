import os
import requests
import streamlit as st

try:
    # Streamlit Community Cloud injects secrets.toml; local runs typically
    # don't have one, and st.secrets raises on any access in that case.
    API_URL = st.secrets["API_URL"]
except Exception:
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

st.header("SSL / HTTP / Weird Features (optional)")
st.caption("Leave as \"-\" if not applicable. These are only present for SSL/HTTP connections.")
col3, col4 = st.columns(2)

with col3:
    ssl_version = st.text_input("ssl_version", value="-")
    ssl_cipher = st.text_input("ssl_cipher", value="-")
    ssl_resumed = st.text_input("ssl_resumed", value="-")
    ssl_established = st.text_input("ssl_established", value="-")
    http_trans_depth = st.text_input("http_trans_depth", value="-")
    http_method = st.text_input("http_method", value="-")

with col4:
    http_version = st.text_input("http_version", value="-")
    http_orig_mime_types = st.text_input("http_orig_mime_types", value="-")
    http_resp_mime_types = st.text_input("http_resp_mime_types", value="-")
    weird_name = st.text_input("weird_name", value="-")
    weird_addl = st.text_input("weird_addl", value="-")
    weird_notice = st.text_input("weird_notice", value="-")

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
    "ssl_version": ssl_version,
    "ssl_cipher": ssl_cipher,
    "ssl_resumed": ssl_resumed,
    "ssl_established": ssl_established,
    "http_trans_depth": http_trans_depth,
    "http_method": http_method,
    "http_version": http_version,
    "http_orig_mime_types": http_orig_mime_types,
    "http_resp_mime_types": http_resp_mime_types,
    "weird_name": weird_name,
    "weird_addl": weird_addl,
    "weird_notice": weird_notice,
}

# The RF pipeline's imputer only fills genuinely missing values (null) with
# its learned most-frequent category. A literal "-" is an unseen category
# and gets encoded as "unknown" instead, so translate the UI's "-" sentinel
# to null before sending.
rf_inputs = {k: (None if v == "-" else v) for k, v in rf_inputs.items()}

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
        if attack_resp.ok:
            attack_data = attack_resp.json()
            if attack_data.get("model_loaded"):
                st.write(attack_data.get("prediction"))
            else:
                st.error("Attack model is not loaded.")
        else:
            st.error(f"Attack request failed ({attack_resp.status_code}): {attack_resp.text}")

        st.subheader("Severity Prediction")
        if severity_resp.ok:
            severity_data = severity_resp.json()
            if severity_data.get("model_loaded"):
                st.write(severity_data.get("prediction"))
            else:
                st.error("Severity model is not loaded.")
        else:
            st.error(f"Severity request failed ({severity_resp.status_code}): {severity_resp.text}")

        st.subheader("Random Forest Prediction")
        if rf_resp.ok:
            rf_data = rf_resp.json()
            if rf_data.get("model_loaded"):
                st.write(rf_data.get("prediction"))
            else:
                st.error("Random forest model is not loaded.")
        else:
            st.error(f"Random forest request failed ({rf_resp.status_code}): {rf_resp.text}")

    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
