import streamlit as st
import pandas as pd
import tempfile
import os
from search import run_email_extraction

st.title("Snov.io Email Extractor")
st.write("Upload a CSV with company names and domains. The app will find emails and let you download the results.")

@st.cache_data(show_spinner=False)
def extract_emails_from_uploaded_file(uploaded_bytes, client, secret):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_input:
        tmp_input.write(uploaded_bytes)
        tmp_input_path = tmp_input.name
    tmp_output_path = tmp_input_path.replace(".csv", "_emails.csv")
    result_path, num_emails = run_email_extraction(tmp_input_path, tmp_output_path, client, secret)

    if result_path:
        with open(result_path, "rb") as f:
            csv_bytes = f.read()
        os.remove(result_path)
    else:
        csv_bytes = None
    os.remove(tmp_input_path)
    return csv_bytes, num_emails

if "client_id" not in st.session_state:
    st.session_state.client_id = ""
    st.session_state.client_secret = ""


client = st.text_input(
        "Snov.io Client ID",
        st.session_state.client_id,
        key="client",
    )

secret = st.text_input(
        "Snov.io Client Secret",
        st.session_state.client_secret,
        key="secret",
    )

if client:
    st.session_state.client_id = client
if secret:
    st.session_state.client_secret = secret

if st.session_state.client_id != "" and st.session_state.client_secret != "":
    st.info("Client ID and Client Secret are set. You can now upload a CSV file to begin.")
    uploaded_file = st.file_uploader("Upload your companies CSV", type=["csv"])

    if uploaded_file is not None:
        with st.spinner("Processing..."):
            csv_bytes, num_emails = extract_emails_from_uploaded_file(uploaded_file.getvalue(), st.session_state.client_id, st.session_state.client_secret)
        if csv_bytes:
            st.success(f"Found {num_emails} emails. Download below:")
            st.download_button(
                label="Download emails.csv",
                data=csv_bytes,
                file_name="emails.csv",
                mime="text/csv"
            )
        else:
            st.warning("No emails found.")
    else:
        st.info("Please upload a CSV file to begin.")