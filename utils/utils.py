import re

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
