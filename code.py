import ast

result = ast.dump(ast.parse("a = -3"))
print(result)
