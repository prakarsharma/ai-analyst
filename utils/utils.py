import re


class clean:
    """
    This class provides methods to clean and format strings.
    It can strip whitespace, ravel (flatten) strings, and extract SQL queries from XML tags.
    It is used to prepare strings for further processing, such as executing SQL queries.
    """
    def __init__(self, string):
        """
        Initializes the object with a string and cleans it by stripping and raveling.
        """
        self.string = clean.strip(clean.ravel(string))

    @staticmethod
    def strip(string:str) -> str:
        """
        Strips leading and trailing whitespace from the string.
        """
        return string.strip().strip("\n").strip()

    @staticmethod
    def ravel(string:str) -> str:
        """
        Flattens the string by removing extra whitespace, newlines, and tabs.
        """
        return re.sub("[\\n\\t\\r ]+", " ", string)

    @staticmethod
    def xml_extract_sql(string:str) -> str:
        """
        Extracts the SQL query from XML tags in the string.
        """
        try:
            return re.findall("<sql>(.*?)</sql>", string)[-1]
        except IndexError as err:
            raise ValueError("!SQL parsing error!")
