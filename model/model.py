import json
from os import listdir, remove
from os.path import isfile, join, realpath, dirname
from sys import argv

class Model:
    def __init__(self) -> None:
        '''
        Model that handles all the data for the app

        self.data is mainly for initialising the app, sending it to the view
        '''
        self.script_directory = dirname(realpath(argv[0]))

        self.data : list = self.retrieve_data()
        self.app_data : dict = self.retrieve_app_data()

        self.data = self.order_data_correctly()

        self.write_to_app_data()

    def retrieve_data(self) -> list:
        data = []

        cur_path = self.script_directory
        files = listdir(join(cur_path, 'data'))
        files.remove('.gitignore')

        for file in files:
            with open(join(cur_path, 'data', file), 'r') as json_file:
                json_data = json.load(json_file)
                json_data['name'] = file.split('.')[0]
                data.append(json_data)

        return data

    def retrieve_app_data(self) -> dict:
        if isfile(join(self.script_directory, "app_data.json")):
            with open(join(self.script_directory, "app_data.json"), 'r') as json_file:
                json_data = json.load(json_file)
                todolist_names = self.get_list_names()

                if len(todolist_names) != 0 and json_data['focused'] not in todolist_names:
                    json_data['focused'] = todolist_names[0]

                for order in json_data['order']:
                    if order not in todolist_names:
                        json_data['order'].remove(order)

                return json_data
        else:
            return {
                'focused': None,
                'order': []
            }

    def order_data_correctly(self) -> list:
        old_data = self.data.copy()
        new_data = []

        if len(old_data) != 0:
            todolists_names = [todolist['name'] for todolist in old_data]
            for list_in_correct_order in self.app_data['order']:
                index_of_todolist = todolists_names.index(list_in_correct_order)
                new_data.append(old_data.pop(index_of_todolist))
                todolists_names.pop(index_of_todolist)
            new_data.extend(old_data)

        return new_data

    def get_list_names(self) -> list:
        if len(self.data) != 0:
            return [i['name'] for i in self.data]
        else:
            return []

    def check_if_todolist_exists(self, list_name) -> bool:
        files = listdir(join(self.script_directory, 'data'))
        if f'{list_name}.json' in files:
            return True
        else:
            return False


    def write_to_app_data(self):
        with open(join(self.script_directory, "app_data.json"), 'w') as json_file:
            json.dump(self.app_data, json_file, indent=4)

    def write_to_todolist_file(self, **kwargs):
        '''
            list_name: name of current focused list
            indices: the list of indices that locate the element being modified
            value: the information being written to the file
            state: whether a task is checked or a section is opened
            action: the type of action that has ocurred

            ### action types:
                - toggle_task
                - toggle_section
                - create_task
                - create_section
                - rename_task
                - clear_checked
                - clear_ all_checked
                - clear_all
        '''

        if 'create' in kwargs['action']:
            self.create_element(**kwargs)
        elif 'toggle' in kwargs['action']:
            self.toggle_element(**kwargs)
        elif 'rename' in kwargs['action']:
            self.rename_element(**kwargs)
        elif 'clear' in kwargs['action']:
            self.clear(**kwargs)
        elif kwargs['action'] == 'delete_element':
            self.delete_element(**kwargs)

    def change_focus(self, list_name):
        self.app_data['focused'] = list_name
        self.write_to_app_data()

    def create_list(self, list_name):
        files = listdir(join(self.script_directory, 'data'))
        files = [file.split('.')[0] for file in files]
        if list_name in files:
            return False
        else:
            todolist_data = {"name": list_name, "data": []}
            with open(join(self.script_directory, 'data', f'{list_name}.json'), 'x') as json_file:
                json.dump({"data": []}, json_file, indent=4)
                self.data.append(todolist_data)
                # self.app_data['focused'] = list_name
            return todolist_data

    def move_list(self, the_list, direction):
        data = self.data
        for todolist in data:
            if todolist['name'] == the_list:
                index_of_list = data.index(todolist)
                data.insert(index_of_list + direction, data.pop(index_of_list))
                break

    def clear(self, list_name, indices=[], action='clear_all') -> None:
        '''
            Deletes tasks in the list or a section based on the action:
            - clear_checked: delete tasks in the same area
            - clear_all_checked: delete all checked tasks in same section and sub sections
            - clear_all: delete every element within it
        '''

        with open(join(self.script_directory, 'data', f"{list_name}.json"), 'r+') as json_file:
            json_data = json.load(json_file)
            json_file.seek(0)

            current_element = json_data['data'] if len(indices) == 0 else json_data['data'][indices[0]]
            
            for i in indices[1:]:
                if isinstance(current_element[0], list):
                    current_element = current_element[1]
                current_element = current_element[i]

            if action == 'clear_all':
                current_element.clear()
            elif action in ('clear_checked', 'clear_all_checked'):
                if len(indices) == 0:
                    new_element = self.clear_checked(current_element, True if action == 'clear_all_checked' else False)
                    current_element.clear()
                    current_element.extend(new_element)
                else:
                    new_element = self.clear_checked(current_element[1], True if action == 'clear_all_checked' else False)
                    current_element[1].clear()
                    current_element[1].extend(new_element)

            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

    def clear_checked(self, the_parent: list, clear_all_checked: bool) -> list:
        '''
            loops through parent and deletes 'tasks' that are checked.

            the_parent is the list the contains the elements.

            Either the entire data of a todolist or the data part of a section.
        '''
        new_parent = []
        for element in the_parent:
            if isinstance(element[1], list):
                if clear_all_checked:
                    element[1] = self.clear_checked(element[1], clear_all_checked)
                new_parent.append(element)
            elif element[1] == False:
                new_parent.append(element)
        return new_parent

    def rename_list(self, old_name, new_name):
        '''
        Assumes that the new file does not exist, creates the new file and places the old data into it, deleting the old json file.
        '''
        
        for todolist in self.data:
            if todolist['name'] == old_name:
                todolist['name'] = new_name
                break

        with open(join(self.script_directory, 'data', f'{old_name}.json'), 'r') as old_file:
            json_data = json.load(old_file)

            with open(join(self.script_directory, 'data', f'{new_name}.json'), 'x') as new_file:
                json.dump(json_data, new_file, indent=4)

        self.delete_list(old_name)

    def delete_list(self, list_name):
        for todolist in self.data:
            if todolist['name'] == list_name:
                self.data.remove(todolist)
        remove(join(self.script_directory, 'data', f'{list_name}.json'))

    def create_element(self, action, list_name, indices, value, state = None):
        with open(join(self.script_directory, 'data', f"{list_name}.json"), 'r+') as json_file:
            json_data = json.load(json_file)
            json_file.seek(0)

            if state is None:
                state = False

            element = [value, state] if 'task' in action else [[value, state], []]
            current_element = json_data['data'] # the root list

            for i in indices[:-1]:
                if i == 0:
                    break
                else:
                    if isinstance(current_element[i][0], str):
                        continue
                    else:
                        current_element = current_element[i][1]

            current_element.insert(indices[-1], element)

            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

    def toggle_element(self, action, list_name, indices, value):
        with open(join(self.script_directory, 'data', f"{list_name}.json"), 'r+') as json_file:
            json_data = json.load(json_file)
            json_file.seek(0)

            current_element = json_data['data'] if len(indices) == 0 else json_data['data'][indices[0]]

            for i in indices[1:]:
                if isinstance(current_element[0], list):
                    current_element = current_element[1]
                current_element = current_element[i]

            if 'task' in action:
                current_element[1] = value
            elif 'section' in action:
                current_element[0][1] = value

            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

    def rename_element(self, action, list_name, indices, value):
        with open(join(self.script_directory, 'data', f"{list_name}.json"), 'r+') as json_file:
            json_data = json.load(json_file)
            json_file.seek(0)

            current_element = json_data['data'] if len(indices) == 0 else json_data['data'][indices[0]]

            for i in indices[1:]:
                if isinstance(current_element[0], list):
                    current_element = current_element[1]
                current_element = current_element[i]

            if 'task' in action:
                current_element[0] = value
            elif 'section' in action:
                current_element[0][0] = value

            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

    def delete_element(self, action, list_name, indices):
        with open(join(self.script_directory, 'data', f"{list_name}.json"), 'r+') as json_file:
            json_data = json.load(json_file)
            json_file.seek(0)

            if len(indices) == 1:
                json_data['data'].pop(indices[0])
            else:
                current_element = json_data['data'] if len(indices) == 0 else json_data['data'][indices[0]]
                indices.pop(0)

                for i in range(len(indices)):
                    if isinstance(current_element[0], list):
                        current_element = current_element[1]

                    if i == len(indices) - 1:
                        current_element.pop(indices[i])
                        break

                    current_element = current_element[indices[i]]
            
            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

    def close_event(self, focused):
        self.app_data['focused'] = focused
        self.app_data['order'] = [i['name'] for i in self.data]
        self.write_to_app_data()