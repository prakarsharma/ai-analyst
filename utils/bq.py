import os
from typing import List, Dict

from utils.utils import clean

class BigQueryJob:
    """
    This class provides an interface to run BigQuery jobs on different platforms.
    It can run queries on Vertex AI or Element platforms.
    It uses the `google.cloud.bigquery` library for Vertex AI and `mlutils.dataset` for Element.
    """
    def __init__(self):
        """
        Initializes the BigQueryJob instance base on the setting of the environment variable `PLATFORM`.
        """
        self.platform = os.environ["PLATFORM"]
        self.create_runner()

    def create_runner(self):
        """
        Creates a runner function to execute BigQuery jobs.
        """
        if self.platform == "vertexai":
            self.runner = create_vertexai_bigquery_client(gcloud_project_id=os.environ["GCLOUD_PROJECT_ID"])
        if self.platform == "element":
            self.runner = create_element_bigquery_connection(bigquery_connection=os.environ["BIGQUERY_CONNECTION"])

    def run(self, query:str) -> List[Dict[str,str]]:
        """
        Runs a BigQuery job with the provided query string.
        :param query: The SQL query to be executed.
        :return: A list of dictionaries containing the results of the query.
        If an error occurs, it returns the error message in a dictionary.
        """
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
    """
    Creates a BigQuery client for Vertex AI.
    :param gcloud_project_id: The Google Cloud project ID.
    :return: A function that runs a BigQuery query.
    """
    from google.cloud import bigquery
    def runner(query:str) -> List[Dict[str,str]]:
        """
        Runs a BigQuery query using the Google Cloud BigQuery client.
        :param query: The SQL query to be executed.
        :return: A list of dictionaries containing the results of the query.
        """
        dataframe = bigquery.Client(project=gcloud_project_id).query(clean(query).string).result().to_dataframe()
        json = dataframe.fillna("").astype(str).to_dict(orient="records")
        return json        
    return runner

def create_element_bigquery_connection(bigquery_connection):
    """
    Creates a BigQuery connection for Element platform.
    :param bigquery_connection: The BigQuery connector name.
    :return: A function that runs a BigQuery query.
    """
    from mlutils import dataset # type: ignore
    def runner(query:str) -> List[Dict[str,str]]:
        """
        Runs a BigQuery query using the Element platform's mlutils package.
        :param query: The SQL query to be executed.
        :return: A list of dictionaries containing the results of the query.
        """
        dataframe = dataset.load(name=bigquery_connection, query=clean(query).string)
        json = dataframe.fillna("").astype(str).to_dict(orient="records")
        return json
    return runner

bigquery_job = BigQueryJob()