import json
from os import path
from pathlib import Path

BASE_PATH = path.join(Path(__file__).parent, "response_files")


class BaseResponseFixture:
    file_path: str = NotImplemented

    def __init__(self, data: dict = None):
        if data is None:
            data = self.load()
        self.data: dict = data

    def __getitem__(self, item: str):
        return self.data[item]

    def load(self):
        return json.load(open(self.get_file_path()))

    def get_file_path(self):
        if self.file_path is NotImplemented:
            raise NotImplementedError
        return self.file_path


class FruitsResponseFixture(BaseResponseFixture):
    file_path = path.join(BASE_PATH, "fruits.json")


class FruitsResponseEmptyDbFixture(BaseResponseFixture):
    file_path = path.join(BASE_PATH, "fruits_empty.json")
