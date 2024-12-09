import os


class Send:
    def __init__(self, obj_list):
        self.objects = obj_list
        self.request_type = None  # 1 - folder, 2 - file
        self.request = None

    def get_request(self, request):
        self.request = request
        self.verification()

    def verification(self):
        if self.request in [i[0] for i in self.get_folders()]:
            self.request_type = 1
        elif '.pdf' in self.request:
            self.request_type = 3
        else:
            self.request_type = 2

    def send_folder(self, request):
        obj = []
        path = None
        for i in self.get_folders():
            if self.request in i:
                path = i[1]
                break

        for dir_path, folder_name, file_name in os.walk(path):
            for folder in folder_name:
                obj.append(folder)
            for file in file_name:
                obj.append(file)

        return obj

    def send_file_text(self, request):
        request += '.txt'
        path = None
        for i in self.get_txt_files():
            if request in i:
                path = i[1]
                break

        with open(path, 'r', encoding='utf-8') as file:
            text = file.read()
            text = text.split('^^^')
            if len(text) > 1:
                return text[1]
            else:
                return text[0]

    def send_document(self, request):
        path = None
        for i in self.get_document():
            if request in i:
                path = i[1]
                break

        with open(path, 'rb') as file:
            data = file.read()
        return data

    def get_txt_files(self):
        return [[i[0], i[1]] for i in self.objects[1] if 'txt' in i[0]]

    def get_document(self):
        return [[i[0], i[1]] for i in self.objects[1] if 'txt' not in i[0]]

    def get_folders(self):
        return self.objects[0]


