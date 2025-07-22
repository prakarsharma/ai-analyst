import os
from typing import Dict


def load_wmt_llm_gateway_secret():
    """
    Loads the WMT LLM Gateway API key from streamlit secrets toml into the environment variable 
    `API_KEY`. It is used for authentication when sending requests to the WMT LLM Gateway API.
    """
    import streamlit as st
    os.environ['API_KEY'] = st.secrets.llm_gateway.api_key

def load_gcloud_oauth_token():
    """
    Loads the Google Cloud OAuth token into the environment variable `ACCESS_TOKEN`.
    It is used for authentication when sending requests to Vertex AI GenAI APIs.
    """
    import google.auth
    import google.auth.transport.requests
    cred, proj = google.auth.default() # cred.valid is False, and cred.token is None
    auth_req = google.auth.transport.requests.Request()
    cred.refresh(auth_req) # need to refresh credentials to populate those
    os.environ['ACCESS_TOKEN'] = cred.token

def authentication() -> Dict[str,str]:
    """
    Returns the API call authentication headers for a specific platform.
    """
    if os.environ["PLATFORM"] == "vertexai":
        load_gcloud_oauth_token()
        access_token:str = os.environ["ACCESS_TOKEN"]
        return {"Authorization": f"Bearer {access_token}"}
    if os.environ["PLATFORM"] == "element":
        load_wmt_llm_gateway_secret()
        api_key:str = os.environ["API_KEY"]
        return {"X-Api-Key": api_key}
    else:
        raise NotImplementedError(f"Platform {os.environ['PLATFORM']} is not supported.")
