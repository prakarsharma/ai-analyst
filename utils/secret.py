import os
from typing import Dict


def load_wmt_llm_gateway_secret():
    import streamlit as st
    os.environ['API_KEY'] = st.secrets.llm_gateway.api_key

def load_gcloud_oauth_token():
    import google.auth
    import google.auth.transport.requests
    cred, proj = google.auth.default() # creds.valid is False, and creds.token is None
    auth_req = google.auth.transport.requests.Request()
    cred.refresh(auth_req) # need to refresh credentials to populate those
    os.environ['ACCESS_TOKEN'] = cred.token

def authentication() -> Dict[str,str]:
    if os.environ["PLATFORM"] == "vertexai":
        load_gcloud_oauth_token()
        access_token:str = os.environ["ACCESS_TOKEN"]
        return {"Authorization": f"Bearer {access_token}"}
    if os.environ["PLATFORM"] == "element":
        load_wmt_llm_gateway_secret()
        api_key:str = os.environ["API_KEY"]
        return {"X-Api-Key": api_key}
