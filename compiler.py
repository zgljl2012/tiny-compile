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

from pprint import pprint
from ast import Str
import re


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

            tokens.append({ 'type': 'number', 'value': value });
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
            tokens.append({ 'type': 'string', 'value': value });
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

if __name__ == '__main__':
    input_ = '(add 1 (sub 2 1))'
    pprint(tokenizer(input_))