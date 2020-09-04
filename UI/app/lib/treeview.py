import os
from collections import OrderedDict


class treeview(object):


    def __init__(self, path):
        self.path = path

    def file_walk(self, root):
        ignore = ['.DS_Store']
        f = []
        for (dirpath, dirnames, filenames) in os.walk(root):
            for file in filenames:
                if file not in ignore:
                    f.append(file)
            break
        print(f)
        tree = OrderedDict()
        tree['/'] = f
        # r=root, d=directories, f = files
        for r, d, f in os.walk(root, topdown=True):
            files = []
            d.sort()
            #print(d)
            #print(f)
            for file in f:
                if file not in ignore:
                    files.append(file)

            # remove root
            path = r.replace(root, '')
            if path == '':
                continue
            tree[path] = files
        return tree


    def dir_structure(self):
        file_dic = self.file_walk(self.path)
        directories = file_dic.keys()
        root = []
        # deepest level of directory
        deep = 0
        for directory_path in directories:
            level = directory_path.count(os.sep)
            if level > deep:
                deep = level

        for depth in range(1, deep + 1):
            for directory_path in directories:
                if directory_path.count(os.sep) == depth:
                    if depth == 1:
                        if directory_path != '/':
                            name = directory_path
                            files = file_dic[directory_path]
                            root.append(OrderedDict([(name, files)]))
                        else:
                             for f in file_dic[directory_path]:
                                root.append(f)
                    else:
                        directory_list = directory_path.split('/')
                        directory_list[1] = '/' + directory_list[1]
                        directory_list.pop(0)
                        # ordered dict of next directory
                        branch = root
                        index = -1
                        for j in range(0, len(directory_list) - 1):
                            for r in range(0, len(branch)):
                                if type(branch[r]) != str and (directory_list[j]) in branch[r].keys():
                                    index = r
                            branch = branch[index][directory_list[j]]
                        files = file_dic[directory_path]
                        name = directory_path
                        branch.append(OrderedDict([(name, files)]))
        return root


    # type: view / tool
    def filter(self, data, request_type):
        if not data:
            return
        for i in range(0, len(data)):
            if type(data[i]) == OrderedDict:
                dic = data[i]
                path = list(dic.keys())[0]
                seg = path.split('/')
                name = seg[len(seg) - 1]
                dic['text'] = name
                dic.move_to_end('text', last=False)
                if request_type == 'view':
                    dic['selectable'] = True
                    if name != 'wip' and name != 'stock':
                        dic['tags'] = [path, 'delete']
                    else:
                        dic['tags'] = [path]
                if request_type == 'tool':
                    if name == 'wip' or name == 'stock':
                        dic['selectable'] = True
                    else:
                        dic['selectable'] = False
                    dic['tags'] = [path]
                dic['nodes'] = dic.pop(path)
                data[i] = dict(dic)
                self.filter(dic['nodes'], request_type)
            elif type(data[i]) == str:
                data[i] = {'text':data[i], 'icon':'glyphicon glyphicon-book', 'selectable':False}
        return


    def get_view(self, type):
        dirs = self.dir_structure()
        self.filter(dirs, type)
        return dirs
