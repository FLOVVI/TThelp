import os
from fuzzywuzzy import fuzz


class Search:
    def __init__(self, request):
        self.request = request
        self.result = list()
        self.objects = self.get_objects()
        if request is not None:
            self.comparison_folder(self.get_folders())
            if len(self.result) != 0:
                for res in self.result:
                    self.comparison_file_name(self.get_file_in_folder(res))
                    self.comparison_file_content(self.get_file_in_folder(res))
                    break

            else:
                self.comparison_file_name(self.get_txt_files())
                self.comparison_file_content(self.get_txt_files())

                if len(self.result) == 0:
                    self.result.append('Ничего не найдено')


    def get_result(self):
        return self.result

    @staticmethod
    def get_objects():
        folders_list = list()
        files_list = list()
        for dir_path, folder_name, file_name in os.walk("Data"):
            # перебрать каталоги
            for i in folder_name:
                folders_list.append([i, os.path.join(dir_path, i)])
            # перебрать файлы
            for j in file_name:
                files_list.append([j, os.path.join(dir_path, j)])

        return folders_list, files_list

    def get_txt_files(self):
        return [[i[0], i[1]] for i in self.objects[1] if 'txt' in i[0]]

    def get_folders(self):
        return self.objects[0]

    # Все файлы в определенной папке
    def get_file_in_folder(self, folder):
        return [[i[0], i[1]] for i in self.get_txt_files() if folder in i[1]]

    # Сравниваем запрос названием папок
    def comparison_folder(self, folders):
        for folder in folders:
            res = fuzz.partial_ratio(folder[0].title(), self.request.title())
            if res >= 80:
                if folder[0] not in self.result:
                    self.result.append(folder[0])

    # Сравниваем запрос с названиями файлов
    def comparison_file_name(self, files):
        for file in files:
            res = fuzz.partial_ratio(file[0].title(), self.request.title())
            if res >= 90:
                if file[0] not in self.result:
                    self.result.append(file[0])

    # Сравниваем запрос с текстом в файлах
    def comparison_file_content(self, files):
        for file in files:
            with open(file[1], 'r', encoding='utf-8') as f:
                res = fuzz.partial_ratio(f.read().title(), self.request.title())
                if res >= 80:
                    if file[0] not in self.result:
                        self.result.append(file[0])