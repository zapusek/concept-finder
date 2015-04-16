import ast

class PyToASTConverter():
    "takes python code as an input and converts it to simplified AST representation tree"
    def __init__(self, python_code):
        self.python_code = python_code
        self.simplified_ast_tree = ""
        self.constructs = ("def", "If", "For", "While", "Return")
        self.function_names = list()
        self.gSpan_graph = ""
        self.nodes = list() #list of all nodes in this ast tree

        node = ast.parse(self.python_code)

        #at first we get names of all function so we can later detect if the function call was made
        for item in node.__dict__["body"]:
            if item.__class__.__name__ == "FunctionDef":
                self.function_names.append(item.__dict__["name"])

        self.ast_visit_my(node)
        #print(self.simplified_ast_tree)
        print("gSpan graph:", self.gSpan_graph)
        print("nodes", self.nodes)

    def get_ast_string_represent(self):
        return self.simplified_ast_tree

    def str_node(self, node):
        if isinstance(node, ast.AST): #preveri če je node instanca razreda ast
            #print("to je pravi node:", node)
            fields = [(name, self.str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]

            if node.__class__.__name__ == "FunctionDef":
                rv_s = "def" + " " + node.__dict__["name"]
            elif node.__class__.__name__ == "NameConstant":
                rv_s = ""
            elif node.__class__.__name__ in ("Name", "Num"):
                rv_s = node.__class__.__name__ +  " = "
            else:
                rv_s = node.__class__.__name__
            #print("Iz tega bo potem sestavil string: ", node, fields)
            for field_name, value in fields:
                #print("node:", node.__class__.__name__, "field_name:", field_name, "value:", value)
                if field_name == "name":
                    pass
                    #rv_s += str(value)
                elif field_name == "arg":
                    rv_s += " " + str(value)
                elif node.__class__.__name__ == "NameConstant":
                    rv_s += str(field_name) + " " + str(value)

                elif node.__class__.__name__ == "Call":
                    #print("klic funkcije", node.__class__.__name__)
                    #print("ime funkcije, ki je poklicala:", node.__dict__["func"].__dict__["id"])
                    print("YYY", node.__dict__)
                    rv_s = "call" + " " + node.__dict__["func"].__dict__["id"]
                    pass

                elif node.__class__.__name__ in ("Name", "Num"):

                    if node.__class__.__name__ == "def":
                        pass
                        #print("YYY", value)

                    if str(value) not in ("Load", "Store"):
                        rv_s += str(value)
                else:
                    pass
                    #rv_s += str(field_name) + str(value)

            #rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
            return rv_s #+ ')'
        else:
            #print("za node:", node, "imamo vrednost", repr(node))
            return repr(node)

    def ast_visit(self, node, level=0):
        if level != 0: print('  ' * level + self.str_node(node))
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    self.ast_visit(item, level=level+1)
            elif isinstance(value, ast.AST):
                self.ast_visit(value, level=level+1)

    def ast_visit_my(self, node, level = 0):
        if self.str_node(node) in self.constructs or self.str_node(node)[4:] in self.function_names or self.str_node(node)[5:] in self.function_names:
            self.simplified_ast_tree += '  ' * level + self.str_node(node) + "\n"
            self.nodes.append(self.str_node(node))

        for field, value in ast.iter_fields(node):  #Yield a tuple of (fieldname, value) for each field in node._fields that is present on node. Each concrete class has an attribute _fields which gives the names of all child nodes.
            if isinstance(value, list): #node ima otroke, torej ni list
                for i, child in enumerate(value):
                    if self.str_node(node) in self.constructs or self.str_node(node)[4:] in self.function_names or self.str_node(node)[5:] in self.function_names:
                            self.gSpan_graph += "e " + str(node) + " " + str(child) + "\n"
                            #self.gSpan_graph += "e " + str(self.nodez.index(node)) + " " + str(self.nodez.index(child)) + " 0 " +"\n"

                    self.ast_visit_my(child, level = level + 1)
            elif isinstance(value, ast.AST):
                self.ast_visit_my(value, level = level + 1)




f = open("c:\\ast_drevesa\\test\\test.py").read()
print(PyToASTConverter(f).get_ast_string_represent())
