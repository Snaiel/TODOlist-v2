import json
import model.dataObjects as dataObjects
from os import listdir, getcwd
from os.path import isfile, join

class Model:
    def __init__(self) -> None:
        self.data = []
        self.app_data = {
            'focused': 'Game'
        }

        self.retrieve_data()

    def retrieve_data(self):
        cur_path = getcwd()
        files = listdir(join(cur_path, 'data'))
        print(files)

        for file in files:
            with open(join(cur_path, 'data', file), 'r') as json_file:
                json_data = json.load(json_file)
                json_data['name'] = file.split('.')[0]
                self.data.append(json_data)

        print(self.data)
    
    def write_to_todolist_file(self, list_name, indices, value):
        with open(join(getcwd(), 'data', f'{list_name}.json'), 'r+') as json_file:
                json_data = json.load(json_file)
                json_file.seek(0)
                element = json_data['data'][indices[-1]]
                for i in reversed(indices[:-1]):
                    if isinstance(element[0], list):
                        element = element[1]
                    element = element[i]
                else:
                    element[1] = value
                json.dump(json_data, json_file, indent=4)
                json_file.truncate()
                




    def get_list_names(self):
        return [i['name'] for i in self.data]

    def change_state(self, list_name, indices):
        for todolist in self.data:
            if todolist['name'] == list_name:
                list_data = todolist['data']
                print('nice', list_data)
                return