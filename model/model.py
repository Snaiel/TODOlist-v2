import json
import model.dataObjects as dataObjects
from os import listdir, getcwd
from os.path import isfile, join

class Model:
    def __init__(self) -> None:
        self.data = [dataObjects.List('Project 1'), dataObjects.List('Side Project')]
        self.app_data = {
            'focused': 'Game'
        }
        self.test_data = []

        self.retrieve_data()

    def retrieve_data(self):
        cur_path = getcwd()
        files = listdir(join(cur_path, 'data'))
        print(files)

        for file in files:
            with open(join(cur_path, 'data', file), 'r') as json_file:
                json_data = json.load(json_file)
                json_data['name'] = file.split('.')[0]
                self.test_data.append(json_data)

        print(self.test_data)

    def get_list_names(self):
        return [i['name'] for i in self.test_data]