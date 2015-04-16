import ast, os
from tkinter import *
from subprocess import *

class FileHandler():
    #Takes all .py files in a specific folder "py_folder"
    def __init__(self, py_folder, path = "/ast_drevesa/"):
        self.py_folder = py_folder
        self.path = path + py_folder + "/"
        self.list_of_parsed_python_codes = []
        self.list_of_python_codes = []

        files_in_folder = os.listdir( self.path )
        for st, file in enumerate(files_in_folder):
            if file[-3:] == ".py":
                self.list_of_python_codes.append(open(self.path + file, 'r').read())
                self.list_of_parsed_python_codes.append(ast.parse(open(self.path + file, 'r').read()))

    def get_list_of_parsed_python_codes(self):
        return self.list_of_parsed_python_codes

    def get_list_of_python_code(self):
        return self.list_of_python_codes

class PyToASTConverter():
    "takes python code as an input and converts it to simplified AST representation tree"
    def __init__(self, python_code):
        self.python_code = python_code
        self.constructs = ("FunctionDef", "If", "For", "While", "Return", "Expr")
        self.link_list = list()

        node = ast.parse(self.python_code)
        self.ast_visit(node)
        self.simplify()

    def get_link_list(self):
        print("self.link_list", self.link_list)
        return self.link_list

    def ast_visit(self, node, level = 0):
        #print('  ' * level + node.__class__.__name__)
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for i, child in enumerate(value):
                    self.link_list.append((node, child))
                    self.ast_visit(child, level = level + 1)
            elif isinstance(value, ast.AST):
                self.link_list.append((node, value))
                self.ast_visit(value, level = level + 1)

    def simplify(self):
        temp_link_list = list()
        label_list = ("", "If", "For", "While", "Return")

        for n1, n2 in self.link_list:
            n1_temp = n1.__class__.__name__
            n2_temp = n2.__class__.__name__

            #Labels: 0-function, 1-If, 2-For, 3-While, 4-Return, 5-function call
            n1_label = 0 #this is label for gSpan representation
            n2_label = 0 #same as above

            if n1_temp not in self.constructs or n2_temp not in self.constructs:
                continue

            #za funkcije
            if n1_temp == "FunctionDef":
                n1_temp = "def " + n1.__dict__["name"]
            elif n2_temp == "FunctionDef":
                n2_temp = "def " + n2.__dict__["name"]

            #za izraze
            if n1_temp == "Expr":
                n1_temp = "call " + n1.__dict__["value"].__dict__["func"].__dict__["id"]
                n1_label = 5
            elif n2_temp == "Expr":
                n2_temp = "call " + n2.__dict__["value"].__dict__["func"].__dict__["id"]
                n2_label = 5

            #za ostalo
            if n1.__class__.__name__ not in ("Expr", "FunctionDef"):
                n1_label = label_list.index(n1_temp)

            if n2.__class__.__name__ not in ("Expr", "FunctionDef"):
                n2_label = label_list.index(n2_temp)

            temp_link_list.append((n1_temp, id(n1), n1_label, n2_temp, id(n2), n2_label))

        self.link_list = temp_link_list

    def get_simplified_ast_tree(self):
        return self.link_list

class ASTToGSpanConverter():
    def __init__(self, link_list):
        self.link_list = link_list
        self.gspan_text_file = ""
        self.vertex_dict = dict()
        self.make_gspan_representation()

    def make_gspan_representation(self):
        vertex_dict = {}
        vertex_number = 0

        #get list of unique vertexes
        for l1, l1_id, l1_label, l2, l2_id, l2_label in self.link_list:
            vertex_dict[l1_id] = [l1, l1_label]
            vertex_dict[l2_id] = [l2, l2_label]

        #setting the vertex numbers
        for key in vertex_dict.keys():
            vertex_dict[key].append("v" + str(vertex_number))
            self.gspan_text_file += "v " + str(vertex_number) + " " + str(vertex_dict[key][1]) +"\n"

            #self.gspan_text_file += "v " + str(vertex_number) + " " + "0" + "\n"
            vertex_number += 1

        #defining edges
        for l1, l1_id, l1_label, l2, l2_id, l2_label in self.link_list:
            self.gspan_text_file += "e " + str(vertex_dict[l1_id][2][1:]) + " " + str(vertex_dict[l2_id][2][1:]) + \
                                    " 0" + "\n"

        self.vertex_dict = vertex_dict

    def get_gspan_representation(self):
        return self.gspan_text_file

    def get_vertex_dict(self):
        return self.vertex_dict

class MakeGSpanInputFile():
    """input is a folder containing .py codes, for each it builds simplified AST tree,
    transforms it to gSpan representation"""
    def __init__(self, py_folder):
        self.py_folder = py_folder
        self.list_of_correct_solutions = list()
        self.list_of_wrong_solutions = list()
        self.gspan_text_file = ""

    def make_gspan_input_file(self):
        f = FileHandler(self.py_folder)
        list_of_python_codes = f.get_list_of_python_code()
        graph_number = 0
        function_number = 6 #for labeling function definitions and calls
        list_of_links = dict()
        gspan_code_text = ""
        function_dict = {"If":1, "For":2, "While":3, "Return":4}

        for i, code in enumerate(list_of_python_codes):
            print("NEW FILE")

            self.gspan_text_file += "t # " + str(i)

            #checks if code is correct or wrong
            for line in code.split("\n"):

                if line[1] == "p":
                    self.list_of_correct_solutions.append(graph_number)
                else:
                    self.list_of_wrong_solutions.append(graph_number)
                break

            list_of_links = PyToASTConverter(code).get_link_list()

            vertex_dict = {}
            vertex_number = 0

            #get list of unique vertexes
            for l1, l1_id, l1_label, l2, l2_id, l2_label in list_of_links:
                vertex_dict[l1_id] = [l1, l1_label]
                vertex_dict[l2_id] = [l2, l2_label]

            print("VERTEX DICT", vertex_dict)

            #setting the vertex labels
            for key in vertex_dict.keys():


                if vertex_dict[key][1] == 0 or vertex_dict[key][1] == 5:

                    if function_dict.get(vertex_dict[key][0], -1) == -1:
                        function_dict[vertex_dict[key][0]] = function_number
                        function_number += 1

                vertex_dict[key].append("v" + str(vertex_number))
                gspan_code_text += "v " + str(vertex_number) + " " + str(function_dict[vertex_dict[key][0]]) +"\n"

                #self.gspan_text_file += "v " + str(vertex_number) + " " + "0" + "\n"
                vertex_number += 1

            #edges
            for l1, l1_id, l1_label, l2, l2_id, l2_label in list_of_links:
                gspan_code_text += "e " + str(vertex_dict[l1_id][2][1:]) + " " + str(vertex_dict[l2_id][2][1:]) + " 0" + "\n"

            self.gspan_text_file += gspan_code_text
            print("gspan text", gspan_code_text)
            print("function dict", function_dict)

        print("GSPAN INPUT FILE:", self.gspan_text_file)






class GSpanRepresent():
    def __init__(self, py_folder):
        self.combined_gspan_represent = ""
        self.py_folder = py_folder
        self.list_of_correct_solutions = list()
        self.list_of_wrong_solutions = list()
        self.get_combined_gspan_represent()

    def get_combined_gspan_represent(self):
        list_of_python_codes = list()
        graph_number = 0

        try:
            f = FileHandler(self.py_folder)
            list_of_python_codes = f.get_list_of_python_code()
            for code in list_of_python_codes:

                for line in code.split("\n"):
                    if line[1] == "p":
                        self.list_of_correct_solutions.append(graph_number)
                    else:
                        self.list_of_wrong_solutions.append(graph_number)
                    break

                self.combined_gspan_represent += "t # " + str(graph_number) + "\n"
                graph_number += 1

                dict_code = ASTToGSpanConverter(PyToASTConverter(code).get_link_list()).get_vertex_dict()

                print("DICT KODE:", dict_code)

                self.combined_gspan_represent += ASTToGSpanConverter(PyToASTConverter(code).get_link_list()).get_gspan_representation()

        except:
            print("Something went wrong best bet is: You have to set the folder that holds .py codes")

    def get_list_of_corr_solutions(self):
        "returns list of indexes of all correct solutions"
        return self.list_of_correct_solutions

    def get_list_of_wrong_solutions(self):
        "returns list of indexes of all wrong solutions"
        return self.list_of_wrong_solutions

    def make_file(self, file_name):
        f = open("gspan_represent_"  + file_name, "w")
        for i, line in enumerate(self.combined_gspan_represent.split("\n")):
            f.write(line + "\n")

class DotViozFromFp():
    def __init__(self):
        self.list_of_corr_solutions = list()
        self.list_of_wrong_solutions = list()
        self.names_of_files_to_delete = []

        self.window = Tk()
        self.canvas = Canvas(self.window, background="white")


        hbar=Scrollbar(self.window,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)

        hbar.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=hbar.set)

        vbar=Scrollbar(self.window,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)

        vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=vbar.set)

    def set_corr_solutions(self, list_of_indexes_of_correct_solutions):
        "start and end index of correct solutions"
        self.list_of_corr_solutions = list_of_indexes_of_correct_solutions

    def set_wrong_solutions(self, list_of_indexes_of_wrong_solutions):
        "start and end index of wrong solutions"
        self.list_of_wrong_solutions = list_of_indexes_of_wrong_solutions

    def set_dictionary_of_vertexes(self, vertex_dict):
        self.vertex_dict = vertex_dict

    def make_list_of_codes(self, fp_file):
        f = open(fp_file, "r")
        subgraphs = list() #list of all subgraphs, input for GRAPHVIZ
        temp_text = ""
        subgraph_for_corr_solutions = list()
        subgraph_for_wrong_solutions = list()
        num_corr_solutions = 0
        num_wrong_solution = 0

        print("prav:", self.list_of_corr_solutions)
        print("narobe:", self.list_of_wrong_solutions)

        for line in f:
            if line[:3] == "t #" and line[4] == "0":
                pass
            elif line[:3] == "t #" and line[4] != "0":
                subgraphs.append((temp_text, (num_corr_solutions, len(self.list_of_corr_solutions)), (num_wrong_solution, len(self.list_of_wrong_solutions))))
                temp_text = ""
                num_corr_solutions = 0
                num_wrong_solution = 0
            elif line[0] == "x":
                for number in line[1:].split():
                    if int(number) in self.list_of_corr_solutions:
                        num_corr_solutions += 1
                    else:
                        num_wrong_solution += 1
                #corr_solutions_ratio = corr_solutions_ratio / len(self.list_of_corr_solutions)
                #wrong_solution_ratio = wrong_solution_ratio / len(self.list_of_wrong_solutions)

            else:
                temp_text += line
        subgraphs.append((temp_text, (num_corr_solutions, len(self.list_of_corr_solutions)), (num_wrong_solution, len(self.list_of_wrong_solutions))))

        subgraphs_temp = list() #clean list of subgraphs from trivial subgraphs

        for code, corr_rat, wrong_rat in subgraphs:
            for line in code.split("\n"):
                if "e" in line:
                    subgraphs_temp.append((code, corr_rat, wrong_rat))
                    break

        print(len(subgraphs_temp), subgraphs_temp)

        return subgraphs_temp

    def from_gspan_to_dotviz(self, code):
        edge_temp_text = ""
        edge_graphs = []
        vertex_graphs = []
        vertex_temp_text = ""
        file_name = "graphviz_input"
        file_number = 0
        construct_names = ("def", "if", "for", "while", "return", "f_call")
        list_of_dotviz_graphs = list()

        for line in code.split("\n"):
            if line and line[0] == "e":
                edge_temp_text += line + "\n"
            elif line and line[0] == "v":
                vertex_temp_text += line + "\n"

        temp_text = "digraph G {\n"
        spaces = "    "
        vertex_names = ["" for e in vertex_temp_text.split("\n")]
        vertex_names.pop()

        for line in vertex_temp_text.split("\n"):
            if line:
                label, v1, v2 = line.split()
                print("label", label, v1, v2)
                vertex_names[int(v1)] = construct_names[int(v2)]

        vertex_names_changed = ["" for e in vertex_names]

        for i, keyword in enumerate(vertex_names):
            if vertex_names.count(keyword) != 1:
                vertex_names_changed[i] = vertex_names[i] + str(vertex_names[:i].count(keyword))
            else:
                vertex_names_changed[i] = vertex_names[i]

        vertex_names = vertex_names_changed

        for line in edge_temp_text.split("\n"):
            if line:
                label1, v1, v2, label2 = line.split()
                temp_text += spaces + vertex_names[int(v1)] + " -> " + vertex_names[int(v2)] + ";\n"

        temp_text += "}"
        return temp_text

    def make_list_of_dotviz_representations_from_gspan_graphs(self, subgraphs):
        self.temp_subgraphs = []
        for code, corr_ratio, wrong_ratio in subgraphs:
            self.temp_subgraphs.append((self.from_gspan_to_dotviz(code), corr_ratio, wrong_ratio))
        return self.temp_subgraphs

    def make_pictures_from_list_of_dotviz_rep(self):
        counter = 0

        for code, corr_ratio, wrong_ratio in self.temp_subgraphs:
            f = open("temp_file.dot", "w")
            f.write(code)
            f.close()
            call(['dot','-Tpng',"temp_file.dot",'-o','OutputFilef'+str(counter)+'.gif'], shell=True)
            self.names_of_files_to_delete.append('OutputFilef'+str(counter)+'.gif')
            counter += 1
            #if counter > 5:
            #    break

    def callback(self):
        for picture in self.names_of_files_to_delete:
            call(['del', picture], shell=True)
        self.window.destroy()
        print("done with deleting pictures")

    def show_pictures(self):
        self.imageList = []  # Store images for cards
        self.labelList = []
        self.picture_set = []
        x = 0
        y = 0
        max_height = 0
        x_offset = 20
        y_offset = 20
        counter = 0
        pictures_size = 0

        screen_width_list = []
        screen_height_list = []
        screen_height = 0
        cnt = -1

        for file in os.listdir(os.curdir):
            if file[-4:] == ".gif":
                self.picture_set.append(PhotoImage(file = file))
                self.canvas.create_image(x, y, image = self.picture_set[-1], anchor=NW)

                num_corr, all_corr = self.temp_subgraphs[cnt][1]
                num_wrong, all_wrong = self.temp_subgraphs[cnt][2]

                if all_corr == 0:
                    text_corr = "P: 0/0 0%"
                else:
                    #print("a to se ne prav izračuna:", num_corr, all_corr, num_corr / all_corr)
                    text_corr = "P: " + str(num_corr) + "/" + str(all_corr) + " " + str(num_corr/all_corr*100) + "%"

                if all_wrong == 0:
                    text_wrong = "N: 0/0 0%"
                else:
                    text_wrong = "N: " + str(num_wrong) + "/" + str(all_wrong) + " " + str(num_wrong/all_wrong*100) + "%"

                cnt += 1

                self.canvas.create_text(x + self.picture_set[-1].width()/2, y + self.picture_set[-1].height() + y_offset, text=text_corr, anchor = CENTER)
                self.canvas.create_text(x + self.picture_set[-1].width()/2, y + self.picture_set[-1].height() + 2*y_offset, text=text_wrong, anchor = CENTER)
                x += self.picture_set[-1].width() + x_offset

                if max_height < self.picture_set[-1].height():
                    max_height = self.picture_set[-1].height()
                counter += 1

                if counter == 5:
                    screen_width_list.append(x)
                    counter = 0
                    x = 0
                    y += max_height + 4*y_offset
                    screen_height += y
                    print("trenutna izračunana višina:", screen_height)
                    max_height = 0
        if counter != 5:
            screen_height += max_height + 4*y_offset

        print("to je višina canvasa, ki se nastavi:", screen_height)

        self.canvas.config(width = max(screen_width_list), height = y)

        self.canvas.config(scrollregion = [0, 0, self.canvas["width"], self.canvas["height"]])
        self.canvas.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.callback)

        self.window.mainloop()

#make
a = MakeGSpanInputFile("test")
a.make_gspan_input_file()
#a.make_file("analiza")

#from .fp file from gSpan to pydot representation of subgraphs
#dot_viz_handler = DotViozFromFp()

#dot_viz_handler.set_corr_solutions(a.get_list_of_corr_solutions())
#dot_viz_handler.set_wrong_solutions(a.get_list_of_wrong_solutions())
#dot_viz_handler.make_list_of_dotviz_representations_from_gspan_graphs(dot_viz_handler.make_list_of_codes("gspan_represent_analiza.fp"))

#visualization of subgraphs
#dot_viz_handler.make_pictures_from_list_of_dotviz_rep()
#dot_viz_handler.show_pictures()