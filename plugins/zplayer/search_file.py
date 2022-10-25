import os


class Search:
    def walk_file(self, folderpath, filename):
        '''
        :param filepath: 项目路径
        :param filename: 待查找的文件名称
        :returns: 
            - full_path_lst: 文件路径列表
            - file_name_lst: 文件名列表
        '''
        full_path_lst = []
        file_name_lst = []
        for root, dirs, files in os.walk(folderpath):
            # root 表示当前正在访问的文件夹路径
            # dirs 表示该文件夹下的子目录名list
            # files 表示该文件夹下的文件list
            for file in files:
                if filename in file:
                    full_path_lst.append(os.path.join(root, file))
                    file_name_lst.append(file)
        return full_path_lst, file_name_lst
