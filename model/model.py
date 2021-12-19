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
    
    def write_to_todolist_file(self, list_name, indices, value, action):
        '''
            list_name: name of current focused list
            indices: the list of indices that locate the element being modified
            value: the information being written to the file
            action: the type of action that has ocurred

            ## action types:
                - toggle_task
                - toggle_section
                - create_task
                - create_section
        '''
        with open(join(getcwd(), 'data', f'{list_name}.json'), 'r+') as json_file:
            json_data = json.load(json_file)
            json_file.seek(0)

            if 'create' in action: # value: the name of the element
                element = [value, False] if 'task' in action else [[value, False], []]
                current_element = json_data['data'] # the root list
                for i in reversed(indices):
                    if i >= len(current_element) or isinstance(current_element[i][0], str):
                        continue
                    else:
                        current_element = current_element[i][1]

                current_element.insert(i, element)

            elif 'toggle' in action:
                current_element = json_data['data'][indices[-1]]
                for i in reversed(indices[:-1]):
                    if isinstance(current_element[0], list):
                        current_element = current_element[1]
                    current_element = current_element[i]

                if action == 'toggle_task':
                    current_element[1] = value
                elif action == 'toggle_section':
                    current_element[0][1] = value

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