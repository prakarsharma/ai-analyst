import os


def load_wmt_ca_bundle():
    """
    Loads the WMT CA bundle into the environment variables for SSL certificate verification.
    It sets the SSL_CERT_FILE and REQUESTS_CA_BUNDLE environment variables to the path of the 
    WMT CA bundle.
    """
    WMT_CA_PATH = "/home/jupyter/.ssl_certs/ca-bundle.crt"
    os.environ['SSL_CERT_FILE'] = WMT_CA_PATH
    os.environ['REQUESTS_CA_BUNDLE'] = WMT_CA_PATH