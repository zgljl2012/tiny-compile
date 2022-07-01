"""

仿自: https://github.com/jamiebuilds/the-super-tiny-compiler/blob/master/the-super-tiny-compiler.js

使用 Python 实现的简单 Lisp 编译器，实现将 Lisp 语言（仅提供 add 和 sub 两个函数）编译为 Python 语言并运行。

编译器的三个主要阶段：

1. Parsing: 将原始代码转化为更抽象的表达式代码
    a. Lexical Analysis
    2. Syntactic Analysis
2. Transformtion
3. Code generation

"""

from multiprocessing.dummy import Array
from pprint import pprint
from ast import Str
import re

"""
词法分析
"""
def tokenizer(input: Str):
    current = 0
    tokens = []
    while current < len(input):
        char = input[current]
        if char == '(':
            tokens.append({
                'type': 'paren',
                'value': '('
            })
            current += 1
            continue
        if char == ')':
            tokens.append({
                'type': 'paren',
                'value': ')',
            })
            current += 1
            continue
        WHITESPACE = re.compile(r'\s')
        if WHITESPACE.match(char):
            current +=1
            continue

        NUMBERS = re.compile(r'[0-9]')
        if NUMBERS.match(char):
            value = ''
            while NUMBERS.match(char):
                value += char
                current += 1
                char = input[current]

            tokens.append({ 'type': 'number', 'value': value })
            continue

        if char == '"':
            value = ''
            current += 1
            char = input[current]
            while char != '"':
                value += char
                current += 1
                char = input[current]
            current += 1
            char = input[current]
            tokens.append({ 'type': 'string', 'value': value })
            continue

        LETTERS = re.compile(r'[a-zA-Z]')
        if LETTERS.match(char):
            value = ''
            while LETTERS.match(char):
                value += char
                current += 1
                char = input[current]
            tokens.append({ 'type': 'name', 'value': value })
            continue

        raise ValueError('I dont know what this character is: ' + char)
    return tokens

"""
语法分析
"""
def parser(tokens):
    current = 0
    def walk():
        nonlocal current # 嵌套闭包需进行此声明
        token = tokens[current]
        if token['type'] == 'number':
            current += 1
            return {
                'type': 'NumberLiteral',
                'value': token['value']
            }
        if token['type'] == 'string':
            current += 1
            return {
                'type': 'StringLiteral',
                'value': token['value']
            }
        if token['type'] == 'paren' and token['value'] == '(':
            current += 1
            token = tokens[current]
            node = {
                'type': 'CallExpression',
                'name': token['value'],
                'params': []
            }
            current += 1
            token = tokens[current]
            while token['type'] != 'paren' or token['type'] == 'paren' and token['value'] != ')':
                node['params'].append(walk())
                token = tokens[current]
            current += 1
            return node
        raise ValueError(type.type)
    ast = {
        'type': 'Program',
        'body': []
    }
    while current < len(tokens):
        ast['body'].append(walk())
    return ast


def traverser(ast, visitor):
    def traverseArray(array: Array, parent):
        for i in array:
            traverseNode(i, parent)
    def traverseNode(node, parent):
        methods = visitor.get(node['type'], None)
        if methods and methods['enter']:
            methods['enter'](node, parent)
        if node['type'] == 'Program':
            traverseArray(node['body'], node)
        elif node['type'] == 'CallExpression':
            traverseArray(node['params'], node)
        elif node['type'] == 'NumberLiteral' or node['type'] == 'StringLiteral':
            pass
        else:
            raise ValueError(node.get('type'))
        if methods and methods.get('exit', None):
            methods['exit'](node, parent)
    traverseNode(ast, None)


def transformer(ast):
    newAst = {
        'type': 'Program',
        'body': []
    }
    ast['_context'] = newAst['body']
    def _callExpressionEnter(node, parent):
        expression = {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': node['name']
            },
            'arguments': []
        }
        node['_context'] = expression['arguments']
        if parent['type'] != 'CallExpression':
            expression = {
                'type': 'ExpressionStatement',
                'expression': expression
            }
        parent['_context'].append(expression)
    traverser(ast, {
        'NumberLiteral': {
            'enter': lambda node, parent: {
                parent['_context'].append({
                    'type': 'NumberLiteral',
                    'value': node['value']
                })
            }
        },
        'StringLiteral': {
            'enter': lambda node, parent: {
                parent['_context'].append({
                    'type': 'StringLiteral',
                    'value': node['value']
                })
            }
        },
        'CallExpression': {
            'enter': _callExpressionEnter
        }
    })
    return newAst


def codeGenerator(node):
    t = node['type']
    if t == 'Program':
        results = []
        for i in node['body']:
            results.append(codeGenerator(i))
        return '\n'.join(results)
    elif t == 'ExpressionStatement':
        return codeGenerator(node['expression'])
    elif t == 'CallExpression':
        results = []
        for i in node['arguments']:
            results.append(codeGenerator(i))
        args = ', ' .join(results)
        return codeGenerator(node['callee']) + '(' + args + ')'
    elif t == 'Identifier':
        return node['name']
    elif t == 'NumberLiteral':
        return node['value']
    elif t == 'StringLiteral':
        return '"' + node['value'] + '"'
    else:
        raise ValueError(node['type'])

def compile(input_):
    tokens = tokenizer(input_)
    ast = parser(tokens)
    newAst = transformer(ast)
    code = codeGenerator(newAst)
    return code

def runtime(compiled):
    def add(a, b):
        return a + b
    def sub(a, b):
        return a - b
    return exec(f'print({compiled})')

def shell():
    print('='*20, 'This is a tiny compile which can compile List to python(only support `add` & `sub`)\ne.g. (add 1 (sub 2 1))', '='*20)
    while True:
        code = input('Code >')
        compiled = compile(code)
        print('Compiled:', compiled)
        print('Result:')
        runtime(compiled)

if __name__ == '__main__':
    shell()
