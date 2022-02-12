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
        self.data = []
        self.app_data = {}

        self.script_directory = dirname(realpath(argv[0]))

        self.retrieve_data()
        self.app_data = self.retrieve_app_data()

        self.data = self.order_data_correctly()

        self.write_to_app_data()

    def retrieve_app_data(self):
        if isfile('app_data.json'):
            with open('app_data.json', 'r') as json_file:
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

    def retrieve_data(self):
        cur_path = self.script_directory
        files = listdir(join(cur_path, 'data'))
        files.remove('.gitignore')

        for file in files:
            with open(join(cur_path, 'data', file), 'r') as json_file:
                json_data = json.load(json_file)
                json_data['name'] = file.split('.')[0]
                self.data.append(json_data)

        # print(self.data)

    def order_data_correctly(self):
        data = self.data
        if len(data) != 0:
            order = self.app_data['order']
            for list_in_correct_position in order:
                data.insert(order.index(list_in_correct_position), data.pop(data.index([i for i in data if i['name'] in order][0])))
            return data
        else:
            return []

    def get_list_names(self):
        if len(self.data) != 0:
            return [i['name'] for i in self.data]
        else:
            return []

    def check_if_todolist_exists(self, list_name):
        files = listdir(join(self.script_directory, 'data'))
        if f'{list_name}.json' in files:
            return True
        else:
            return False


    def write_to_app_data(self):
        with open('app_data.json', 'w') as json_file:
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
                - delete_element
                - clear_checked
                - clear_ all_checked
                - clear_all
        '''
        if 'state' not in kwargs:
            kwargs['state'] = False

        with open(join(self.script_directory, 'data', f"{kwargs['list_name']}.json"), 'r+') as json_file:
            json_data = json.load(json_file)
            json_file.seek(0)

            # print(kwargs['action'])

            if 'create' in kwargs['action']: # value: the name of the element
                element = [kwargs['value'], kwargs['state']] if 'task' in kwargs['action'] else [[kwargs['value'], kwargs['state']], []]
                current_element = json_data['data'] # the root list

                for i in range(len(kwargs['indices']) - 1, -1, -1):
                    if i == 0:
                        break
                    else:
                        if isinstance(current_element[kwargs['indices'][i]][0], str):
                            continue
                        else:
                            current_element = current_element[kwargs['indices'][i]][1]

                current_element.insert(kwargs['indices'][i], element)
            else:
                # print(kwargs['action'], kwargs['indices'])
                if kwargs['action'] == 'delete_element' and len(kwargs['indices']) == 1:
                    json_data['data'].pop(kwargs['indices'][0])
                else:
                    # current_element = json_data['data'][kwargs['indices'][-1]]
                    current_element = json_data['data'] if len(kwargs['indices']) == 0 else json_data['data'][kwargs['indices'][-1]]

                    for i in range(len(kwargs['indices'])-1):
                        if isinstance(current_element[0], list):
                            current_element = current_element[1]

                        # print(kwargs['action'], current_element, kwargs['indices'], list(reversed(kwargs['indices'][:-1])), i)
                        if kwargs['action'] == 'delete_element' and i == len(kwargs['indices']) - 2:
                            current_element.pop(list(reversed(kwargs['indices'][:-1]))[i])
                            break

                        current_element = current_element[list(reversed(kwargs['indices'][:-1]))[i]]

                    if kwargs['action'] == 'toggle_task':
                        current_element[1] = kwargs['value']
                    elif kwargs['action'] == 'toggle_section':
                        current_element[0][1] = kwargs['value']
                    elif kwargs['action'] == 'rename_task':
                        current_element[0] = kwargs['value']
                    elif kwargs['action'] == 'rename_section':
                        current_element[0][0] = kwargs['value']
                    elif kwargs['action'] == 'clear_all':
                        current_element[1] = []
                    elif kwargs['action'] in ('clear_checked', 'clear_all_checked'):
                        print('clear brotha', current_element)
                        if len(kwargs['indices']) == 0:
                            current_element = self.clear_checked(current_element, True if kwargs['action'] == 'clear_all_checked' else False)
                        else:
                            current_element[1] = self.clear_checked(current_element[1], True if kwargs['action'] == 'clear_all_checked' else False)

            


            json.dump(json_data, json_file, indent=4)
            json_file.truncate()

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

    def clear(self, focused_list, indices=[], clear_type='All'):
        '''
            Deletes tasks based on the clear_type:
            - Checked: delete tasks in the same area
            - All Checked: delete all checked tasks in same section and sub sections
            - All: delete every element within it
        '''

        if clear_type == 'Checked':
            self.write_to_todolist_file(list_name=focused_list, indices=indices, action='clear_checked')
        elif clear_type == 'All Checked':
            self.write_to_todolist_file(list_name=focused_list, indices=indices, action='clear_all_checked')
        elif clear_type == 'All':
            if not indices:
                with open(join(self.script_directory, 'data', f'{focused_list}.json'), 'w') as json_file:
                    json.dump({"data": []}, json_file, indent=4)
            else:
                self.write_to_todolist_file(list_name=focused_list, indices=indices, action='clear_all')

    def clear_checked(self, the_parent, clear_all_checked):
        '''
            loops through parent and deletes 'tasks' that are checked
        '''
        new_parent = []
        for element in the_parent:
            print(element)
            if isinstance(element[1], list) and clear_all_checked:
                element[1] = self.clear_checked(element[1], clear_all_checked)
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

    def close_event(self, focused):
        self.app_data['focused'] = focused
        self.app_data['order'] = [i['name'] for i in self.data]
        self.write_to_app_data()