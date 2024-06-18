import os


def load_wmt_ca_bundle():
    WMT_CA_PATH = "/home/jupyter/.ssl_certs/ca-bundle.crt"
    os.environ['SSL_CERT_FILE'] = WMT_CA_PATH
    os.environ['REQUESTS_CA_BUNDLE'] = WMT_CA_PATH