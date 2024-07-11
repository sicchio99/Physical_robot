import json

PATH = "./"


class ReadConfig:
    _file_content: dict

    def __init__(self):
        with open(f'{PATH}config.json', 'r') as f:
            self._file_content = json.loads(f.read())

    def read_data(self, data_to_read):
        return self._file_content[data_to_read]