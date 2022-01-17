import json
from os import listdir, getcwd, remove
from os.path import isfile, join

class Model:
    def __init__(self) -> None:
        '''
        Model that handles all the data for the app

        self.data is mainly for initialising the app, sending it to the view
        '''
        self.data = []
        self.app_data = {}
        # self.app_data = {
        #     'focused': 'Game'
        # }

        self.retrieve_data()
        self.app_data = self.retrieve_app_data()

        self.data = self.order_data_correctly()

        self.write_to_app_data()

    def retrieve_app_data(self):
        with open('app_data.json', 'r') as json_file:
            json_data = json.load(json_file)
            todolist_names = self.get_list_names()

            if json_data['focused'] not in todolist_names:
                json_data['focused'] = todolist_names[0]

            for order in json_data['order']:
                if order not in todolist_names:
                    json_data['order'].remove(order)

            return json_data

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

    def order_data_correctly(self):
        data = self.data
        order = self.app_data['order']
        for list_in_correct_position in order:
            data.insert(order.index(list_in_correct_position), data.pop(data.index([i for i in data if i['name'] in order][0])))
        return data

    def get_list_names(self):
        return [i['name'] for i in self.data]

    def check_if_todolist_exists(self, list_name):
        files = listdir(join(getcwd(), 'data'))
        if f'{list_name}.json' in files:
            return True
        else:
            return False


    def write_to_app_data(self):
        with open('app_data.json', 'w') as json_file:
            json.dump(self.app_data, json_file, indent=4)

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

    def change_focus(self, list_name):
        self.app_data['focused'] = list_name
        self.write_to_app_data()

    def create_list(self, list_name):
        files = listdir(join(getcwd(), 'data'))
        files = [file.split('.')[0] for file in files]
        if list_name in files:
            return False
        else:
            todolist_data = {"name": list_name, "data": []}
            with open(join(getcwd(), 'data', f'{list_name}.json'), 'x') as json_file:
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

    def clear_list(self, focused_list):
        with open(join(getcwd(), 'data', f'{focused_list}.json'), 'w') as json_file:
            json.dump({"data": []}, json_file, indent=4)

    def rename_list(self, old_name, new_name):
        '''
        Assumes that the new file does not exist, creates the new file and places the old data into it, deleting the old json file.
        '''
        
        for todolist in self.data:
            if todolist['name'] == old_name:
                todolist['name'] = new_name
                break

        with open(join(getcwd(), 'data', f'{old_name}.json'), 'r') as old_file:
            json_data = json.load(old_file)

            with open(join(getcwd(), 'data', f'{new_name}.json'), 'x') as new_file:
                json.dump(json_data, new_file, indent=4)

        self.delete_list(old_name)

    def delete_list(self, list_name):
        for todolist in self.data:
            if todolist['name'] == list_name:
                self.data.remove(todolist)
        remove(join(getcwd(), 'data', f'{list_name}.json'))

    def close_event(self, focused):
        self.app_data['focused'] = focused
        self.app_data['order'] = [i['name'] for i in self.data]
        self.write_to_app_data()