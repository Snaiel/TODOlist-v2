class TODOlist:
    def __init__(self, list_name) -> None:
        self.list_name = list_name
        self.list_data = {}

    def rename_list(self, new_name):
        self.list_name = new_name

    def clear_list(self):
        self.list_data = {}

class Section:
    def __init__(self, section_name, section_data) -> None:
        self.section_name = section_name
        self.section_data = section_data

class Task:
    def __init__(self, task_name, task_data) -> None:
        self.task_name = task_name
        self.task_data = task_data

    def rename_task(self, new_name):
        self.task_name = new_name

    

