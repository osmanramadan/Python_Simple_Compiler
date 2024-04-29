import re

class Lexer:
    def __init__(self, code):
        self.code = code
        self.patterns = [
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),  # Identifiers
            (r'\d+', 'NUMBER'),                          # Numbers
            (r'[-+*/=(),]', 'OPERATOR'),                 # Operators and punctuation
            (r'"[^"]*"', 'STRING'),                      # Strings
            (r'#.*', 'COMMENT')                          # Comments
        ]
        self.tokens = self.tokenize()
    
    def tokenize(self):
        tokens = []
        pos = 0
        
        while pos < len(self.code):
            match = None
            for pattern, token_type in self.patterns:
                regex = re.compile(pattern)
                match = regex.match(self.code, pos)
                if match:
                    value = match.group(0)
                    if token_type != 'COMMENT':
                        tokens.append((token_type, value))
                    break
            if not match:
                # Catch-all pattern for handling invalid characters
                tokens.append(('INVALID', self.code[pos]))
                pos += 1
            else:
                pos = match.end()
        
        return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = -1
        self.advance()
    
    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None
    
    def eat(self, token_type):
        if self.current_token and self.current_token[0] == token_type:
            self.advance()
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token[0]}")
    
    def factor(self):
        token = self.current_token
        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return ('number', token[1])
        elif token[0] == 'IDENTIFIER':
            self.eat('IDENTIFIER')
            return ('identifier', token[1])
        elif token[0] == 'STRING':
            self.eat('STRING')
            return ('string', token[1])
        elif token[0] == '(':
            self.eat('(')
            expr = self.expr()
            self.eat(')')
            return expr
    
    def term(self):
        node = self.factor()
        while self.current_token and self.current_token[0] in ('*', '/'):
            if self.current_token[0] == '*':
                op = 'mul'
            else:
                op = 'div'
            self.advance()
            node = ('binop', op, node, self.factor())
        return node
    
    def expr(self):
        node = self.term()
        while self.current_token and self.current_token[0] in ('+', '-'):
            if self.current_token[0] == '+':
                op = 'add'
            else:
                op = 'sub'
            self.advance()
            node = ('binop', op, node, self.term())
        return node

class OrderedSymbolTable:
    def __init__(self):
        self.symbols = []
    
    def add_symbol(self, name, value):
        self.symbols.append((name, value))
    
    def get_symbol(self, name):
        for symbol in self.symbols:
            if symbol[0] == name:
                return symbol[1]
        return None

class UnorderedSymbolTable:
    def __init__(self):
        self.symbols = {}
    
    def add_symbol(self, name, value):
        self.symbols[name] = value
    
    def get_symbol(self, name):
        return self.symbols.get(name, None)

class TreeNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.left = None
        self.right = None

class TreeStructuredSymbolTable:
    def __init__(self):
        self.root = None
    
    def add_symbol(self, name, value):
        if not self.root:
            self.root = TreeNode(name, value)
        else:
            self._add_symbol_recursively(self.root, name, value)
    
    def _add_symbol_recursively(self, node, name, value):
        if name < node.name:
            if node.left:
                self._add_symbol_recursively(node.left, name, value)
            else:
                node.left = TreeNode(name, value)
        elif name > node.name:
            if node.right:
                self._add_symbol_recursively(node.right, name, value)
            else:
                node.right = TreeNode(name, value)
    
    def get_symbol(self, name):
        return self._get_symbol_recursively(self.root, name)
    
    def _get_symbol_recursively(self, node, name):
        if not node:
            return None
        elif name == node.name:
            return node.value
        elif name < node.name:
            return self._get_symbol_recursively(node.left, name)
        else:
            return self._get_symbol_recursively(node.right, name)

class HashSymbolTable:
    def __init__(self, size):
        self.size = size
        self.table = [None] * size
    
    def hash_function(self, key):
        return hash(key) % self.size
    
    def add_symbol(self, name, value):
        index = self.hash_function(name)
        if not self.table[index]:
            self.table[index] = [(name, value)]
        else:
            for i, (existing_name, existing_value) in enumerate(self.table[index]):
                if existing_name == name:
                    self.table[index][i] = (name, value)
                    return
            self.table[index].append((name, value))
    
    def get_symbol(self, name):
        index = self.hash_function(name)
        bucket = self.table[index]
        if bucket:
            for existing_name, value in bucket:
                if existing_name == name:
                    return value
        return None

def main():
    # code = 'x = 10 + 5 * 2'
    with open('C:/Users/osman/Desktop/compiler/code_file.txt', 'r') as file:
   
        code = file.read()

    
    lexer = Lexer(code)
    tokens = lexer.tokens
    print("Tokens lexing:", tokens)
    
    # Parsing
    parser = Parser(tokens)
    parse_tree = parser.expr()
    print("Parse tree:", parse_tree)
    
    # Ordered Symbol Table
    ordered_sym_table = OrderedSymbolTable()
    ordered_sym_table.add_symbol('x', {'counter': 1, 'variable_name': 'x', 'object_address': '0x0001', 'type': 'int', 'dimension': None, 'line_direction': 'horizontal', 'line_reference': None})
    print("Value of x:", ordered_sym_table.get_symbol('x'))
    
    # Unordered Symbol Table
    unordered_sym_table = UnorderedSymbolTable()
    unordered_sym_table.add_symbol('y', {'counter': 2, 'variable_name': 'y', 'object_address': '0x0002', 'type': 'int', 'dimension': None, 'line_direction': 'horizontal', 'line_reference': None})
    print("Value of y:", unordered_sym_table.get_symbol('y'))
    
    # Tree Structured Symbol Table
    tree_sym_table = TreeStructuredSymbolTable()
    tree_sym_table.add_symbol('z', {'counter': 3, 'variable_name': 'z', 'object_address': '0x0003', 'type': 'int', 'dimension': None, 'line_direction': 'horizontal', 'line_reference': None})
    print("Value of z:", tree_sym_table.get_symbol('z'))
    
    # Hash Symbol Table
    hash_sym_table = HashSymbolTable(10)
    hash_sym_table.add_symbol('w', {'counter': 4, 'variable_name': 'w', 'object_address': '0x0004', 'type': 'int', 'dimension': None, 'line_direction': 'horizontal', 'line_reference': None})
    print("Value of w:", hash_sym_table.get_symbol('w'))

if __name__ == "__main__":
    main()
