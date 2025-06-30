import os
import re
from google.cloud import storage
from typing import List, Dict


def read_gcs_file(uri: str) -> str:
    """
    Reads the contents of a file stored in a GCS bucket.
    :param uri: The gsutil URI of the file.
    :return: The contents of the file as a string.
    """
    if not uri.startswith("gs://"):
        raise TypeError("Invalid GCS URI.")
    filename = re.sub(r"^gs://", "", uri)
    parts = filename.split("/", 1)
    if len(parts) != 2:
        raise FileNotFoundError("Invalid file URI.")
    bucket_name, blob_name = parts
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_text()

def chmod_R(path, mode):
    for root, dirs, files in os.walk(path):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            os.chmod(full_path, mode)


class clean:
    def __init__(self, string):
        self.string = clean.strip(clean.ravel(string))

    @staticmethod
    def strip(string:str) -> str:
        return string.strip().strip("\n").strip()

    @staticmethod
    def ravel(string:str) -> str:
        return re.sub("[\\n\\t\\r ]+", " ", string)

    @staticmethod
    def xml_extract_sql(string:str) -> str:
        try:
            return re.findall("<sql>(.*?)</sql>", string)[-1]
        except IndexError as err:
            raise ValueError("!SQL parsing error!")


class BigQueryJob:
    def __init__(self):
        self.platform = os.environ["PLATFORM"]
        self.create_runner()

    def create_runner(self):
        if self.platform == "vertexai":
            self.runner = create_vertexai_bigquery_client(gcloud_project_id=os.environ["GCLOUD_PROJECT_ID"])
        if self.platform == "element":
            self.runner = create_element_bigquery_connection(bigquery_connection=os.environ["BIGQUERY_CONNECTION"])

    def run(self, query:str) -> List[Dict[str,str]]:
        try:
            return self.runner(query)
        except Exception as err:
            # raise ConnectionError("!bigquery job failure!")
            return [
                {
                "error": str(err)
                }
            ]


def create_vertexai_bigquery_client(gcloud_project_id:str):
    from google.cloud import bigquery
    def runner(query:str) -> List[Dict[str,str]]:
        dataframe = bigquery.Client(project=gcloud_project_id).query(clean(query).string).result().to_dataframe()
        json = dataframe.fillna("").astype(str).to_dict(orient="records")
        return json        
    return runner

def create_element_bigquery_connection(bigquery_connection):
    from mlutils import dataset # type: ignore
    def runner(query:str) -> List[Dict[str,str]]:
        dataframe = dataset.load(name=bigquery_connection, query=clean(query).string)
        json = dataframe.fillna("").astype(str).to_dict(orient="records")
        return json
    return runner

bigquery_job = BigQueryJob()