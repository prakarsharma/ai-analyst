import json
import pandas as pd
from io import BytesIO
from matplotlib import pyplot as plt
from typing import List, Dict, Optional

from utils.config import conf
from utils.utils import bigquery_job
from utils.logging import logger


class Tools:
    def __init__(self, use_reminder:bool=True):
        """
        Initialize the Tools class with default values.
        """
        self.use_reminder = use_reminder
        if self.use_reminder:
            logger.info("Sending a reminder at query generation")
        else:
            logger.info("Disabling reminders at query generation")

    def fetch_data(self, table_id:List[str], query:str, max_rows:int=200, **kwargs) -> List[Dict[str,str]]:
        """
        This function fetches data from a BigQuery table using the provided query.
        Ensure that you have the table IDs before you call this function. Call 'get_bigquery_table' to get the table IDs.
        :param table_id: The IDs of the BigQuery tables to query.
        :param query: The SQL query to execute on the BigQuery table.
        :return: A list of dictionaries containing the queried data or an error message.
        :raises ValueError: If the table ID does not match the expected table ID in the configuration.
        """
        logger.info("Using tool 'fetch_data' with arguments:\n table_id = {},\n query = {}", "\n".join(table_id), query)
        metadata = [metadata["table_id"] for table, metadata in conf["bigquery"]["tables"].items()]
        if not all([table in metadata for table in table_id]):
            return [
                {
                "error": f"'{table_id}' is not the correct table ID. Call 'get_bigquery_table' to get the correct table ID."
                }
            ]
        results = bigquery_job.run(query)
        if len(results) > max_rows:
            results = [
                {
                "error": f"Query returned more than {max_rows} rows. Please refine your query."
                }
            ]
        reminder = {
            "warning": """Verify that the generated query is correct. Reconsider the following rules you should follow to generate correct SQL.
            1. Aggregate depending on the grain of data.
            2. Deduplicate any string or date type columns in the select statement if there is no aggregation.
            3. Follow the rule of ratio of averages if a metric is a ratio.
            4. Round to 2 decimal places if the expected result is float type.
            5. Avoid zero-division error.
            6. Use only the provided metrics definitions. Calculate all the required metrics.
            Make corrections, if any, and call 'fetch_data' again."""
        }
        for item in results:
            if "error" in item:
                if self.use_reminder:
                    item.update(reminder)
                    return results
        return results

    def get_bigquery_table(self, **kwargs) -> Dict:
        """
        This function gets the bigquery table IDs and related metadata.
        :return: A dictionary containing the BigQuery table IDs and metadata.
        """
        logger.info("Using tool 'get_bigquery_table'")
        metadata = conf["bigquery"]["tables"]
        return metadata

    def table(self, query:str, records:List[Dict]) -> pd.DataFrame:
        """
        This function makes a table from the records returned by a BigQuery job. This function uses a pandas DataFrame as the choice of tabular data structure.
        :param query: The SQL query that was executed to fetch the records.
        :param records: A list of dictionaries containing the records fetched from the BigQuery table.
        :return: A pandas DataFrame containing the records.
        """
        logger.info("Using tool 'table' with arguments:\n query = {},\n records = {}", query, json.dumps(records, indent=4))
        return pd.DataFrame(records)

    def plot(self, 
             title:str, 
             x:List, 
             xlabel:str, 
             y:Optional[List]=None, 
             ylabel:str="", 
             plot_type:str="scatter", 
             figsize:tuple[float, float]=(10,6)):
        """
        This function generates a plot based on the provided data and parameters. It uses matplotlib to create the plot.
        It supports various plot types such as line, scatter, bar, boxplot, histogram, and pie chart.
        :param title: The title of the plot.
        :param x: A list of data to plot on the x-axis.
        :param xlabel: A suitable name for the data on the x-axis.
        :param y: A list of data to plot on the y-axis (optional).
        :param ylabel: A suitable name for the data on the y-axis (optional).
        :param plot_type: The type of plot to generate (e.g., "line", "scatter", "bar", "boxplot", "histogram", "pie").
        :param figsize: The size of the figure (default is (10, 6)).
        :return: A BytesIO object containing the plot image.
        """
        logger.info("Using tool 'plot' with arguments:\n title = {},\n x = {},\n xlabel = {},\n y = {},\n ylabel = {},\n plot_type = {},\n figsize = {}", title, x, xlabel, y, ylabel, plot_type, figsize)
        buf = BytesIO()
        df = pd.Series(x, name=xlabel).to_frame()
        fig = plt.figure(figsize=figsize)
        plt.suptitle(title)
        plt.xlabel(xlabel)
        if y is not None:
            y_series = pd.Series(y).astype(float)
            if ylabel:
                df[ylabel] = y_series
                plt.ylabel(ylabel)
        df.sort_values(by=xlabel, ascending=True, inplace=True)
        try:
            if plot_type == "line":
                plt.plot(df[xlabel], df[ylabel])
            if plot_type == "scatter":
                plt.scatter(df[xlabel], df[ylabel])
            if plot_type == "bar":
                plt.bar(df[xlabel], df[ylabel])
            if plot_type == "boxplot":
                plt.boxplot(df[xlabel])
            if plot_type == "histogram":
                plt.hist(df[xlabel])
            if plot_type == "pie":
                plt.pie(df[xlabel])
            fig.savefig(buf, format="png")
            return buf
        except KeyError as err:
            return {
                "error": "provide both x and y to make the plot: either one of the axes is missing or can't be computed"
            }

    def EOS(self, message:str) -> str:
        """
        This function indicates the end of response generation.
        Call this function when you want to interact with the user. You can return your final response to the user or use this function to ask a clarifying question.
        :param message: The message to return to the user.
        :return: The message to return to the user.
        """
        logger.info("Using tool 'EOS' with arguments:\n message = {}", message)
        return message