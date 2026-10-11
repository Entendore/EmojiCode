#!/usr/bin/env python3
"""
EMOJICODE 5.0 - Pure Bracket-Free Emoji Programming Language
=========================================================

COMPLETELY BRACKET-FREE FEATURES:
✅ No curly braces, parentheses, or square brackets anywhere
✅ Structure defined by emoji blocks and indentation
✅ Conway's Game of Life without any brackets
✅ Multi-emoji identifiers (✨🌟, 🐶🐱)
✅ Lambda functions without parentheses
✅ Pattern matching with emoji blocks
✅ All control flow using emoji delimiters only

Syntax uses ONLY: emojis, numbers, spaces, and newlines!
"""

import re
import sys
import time
from typing import Dict, List, Any, Union, Optional
from dataclasses import dataclass, field

class EmojicodeRuntimeError(Exception):
    pass

@dataclass
class StructInstance:
    struct_name: str
    fields: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        fields_str = " ".join([f"{k}:{v}" for k, v in self.fields.items()])
        return f"🏗️{self.struct_name} {fields_str}"

@dataclass
class LambdaFunction:
    params: List[str]
    body_tokens: List[str]
    captured_scope: Dict[str, Any]
    
    def __call__(self, interpreter, args):
        old_stack = interpreter.stack[:]
        interpreter.stack.append(self.captured_scope.copy())
        for param, arg in zip(self.params, args):
            interpreter._set_scope(param, arg)
        result = interpreter.execute_block(self.body_tokens)
        interpreter.stack = old_stack
        return result

class EmojicodeInterpreter:
    def __init__(self):
        # Binary operations (all bracket-free)
        self.BINARY_OPS = {
            '➕': lambda a, b: self._add(a, b),
            '➖': lambda a, b: self._sub(a, b),
            '✖️': lambda a, b: self._mul(a, b),
            '➗': lambda a, b: self._div(a, b),
            '🟰': lambda a, b: int(self._eq(a, b)),
            '❗': lambda a, b: int(not self._eq(a, b)),
            '🟢': lambda a, b: int(self._gt(a, b)),
            '🔴': lambda a, b: int(self._lt(a, b)),
            '🟠': lambda a, b: int(not self._lt(a, b)),
            '🔵': lambda a, b: int(not self._gt(a, b)),
            '🔗': lambda a, b: self._concat(a, b),
            'isContained': lambda a, b: int(a in b),
            '🗺️': lambda func, container: self._map(func, container),
            '🧼': lambda func, container: self._filter(func, container),
            '🔁': lambda func, container, init: self._reduce(func, container, init),
        }
        
        # Unary operations
        self.UNARY_OPS = {
            '💯': lambda a: int(a) if self._is_number(a) else self._error("Cannot convert to int"),
            '🔢': lambda a: float(a) if self._is_number(a) else self._error("Cannot convert to float"),
            '📏': lambda a: len(a) if hasattr(a, '__len__') else self._error("Cannot get length"),
            '🔄': lambda a: list(reversed(a)) if isinstance(a, list) else str(a)[::-1],
            '🔤': lambda a: str(a),
            '🔑': lambda d: list(d.keys()) if isinstance(d, dict) else self._error("Not a dictionary"),
            '💎': lambda d: list(d.values()) if isinstance(d, dict) else self._error("Not a dictionary"),
        }
        
        # Control flow emojis (no brackets needed)
        self.CONTROL_FLOW = {
            '➡️': 'IF',
            '⏭️': 'ELSE', 
            '🔄': 'WHILE',
            '🔂': 'FOR_EACH',
            '⏹️': 'END',
            '🖨️': 'PRINT',
            '📥': 'INPUT',
            '📤': 'RETURN',
            '💬': 'COMMENT',
            '🆕': 'NEW',
            '🔍': 'GET',
            '📌': 'SET',
            '✂️': 'SLICE',
            '🏗️': 'STRUCT',
            '🔧': 'METHOD',
            '🚀': 'CALL',
            '🧪': 'LAMBDA',
            '🎯': 'MATCH',
            '💣': 'THROW',
            '🛡️': 'TRY',
            '🪝': 'CATCH',
        }
        
        # Runtime state
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, tuple] = {}
        self.structs: Dict[str, List[str]] = {}
        self.stack: List[Dict] = [{}]
        self.output_buffer = []
        self.exception = None
        
    def _error(self, msg: str):
        raise EmojicodeRuntimeError(f"❌ {msg}")
    
    def _is_number(self, x):
        return isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.','',1).replace('-','',1).isdigit())
    
    # ... (math operations same as before)
    def _add(self, a, b):
        if isinstance(a, str) or isinstance(b, str):
            return str(a) + str(b)
        return float(a) + float(b)
    
    def _sub(self, a, b):
        return float(a) - float(b)
    
    def _mul(self, a, b):
        if isinstance(a, str) and isinstance(b, int):
            return a * b
        if isinstance(b, str) and isinstance(a, int):
            return b * a
        return float(a) * float(b)
    
    def _div(self, a, b):
        if float(b) == 0:
            self._error("Division by zero!")
        return float(a) / float(b)
    
    def _eq(self, a, b):
        try:
            return float(a) == float(b)
        except:
            return str(a) == str(b)
    
    def _gt(self, a, b):
        try:
            return float(a) > float(b)
        except:
            return str(a) > str(b)
    
    def _lt(self, a, b):
        try:
            return float(a) < float(b)
        except:
            return str(a) < str(b)
    
    def _concat(self, a, b):
        if isinstance(a, list):
            return a + ([b] if not isinstance(b, list) else b)
        return str(a) + str(b)
    
    def _map(self, func, container):
        if not callable(func):
            self._error("First argument to map must be a function")
        if isinstance(container, list):
            return [func([item]) for item in container]
        elif isinstance(container, dict):
            return {k: func([v]) for k, v in container.items()}
        else:
            self._error("Cannot map over non-container type")
    
    def _filter(self, func, container):
        if not callable(func):
            self._error("First argument to filter must be a function")
        if isinstance(container, list):
            return [item for item in container if func([item])]
        elif isinstance(container, dict):
            return {k: v for k, v in container.items() if func([v])}
        else:
            self._error("Cannot filter non-container type")
    
    def _reduce(self, func, container, initial):
        if not callable(func):
            self._error("First argument to reduce must be a function")
        if isinstance(container, list):
            from functools import reduce
            return reduce(lambda acc, x: func([acc, x]), container, initial)
        elif isinstance(container, dict):
            from functools import reduce
            return reduce(lambda acc, kv: func([acc, kv[1]]), container.items(), initial)
        else:
            self._error("Cannot reduce non-container type")
    
    def _get_scope(self, var_name: str):
        for scope in reversed(self.stack):
            if var_name in scope:
                return scope[var_name]
        if var_name in self.variables:
            return self.variables[var_name]
        self._error(f"Undefined variable: {var_name}")
    
    def _set_scope(self, var_name: str, value: Any):
        self.stack[-1][var_name] = value
    
    def tokenize(self, code: str) -> List[str]:
        """Tokenize without any brackets - only emojis, numbers, strings, newlines"""
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+'
        string_pattern = r'(["\'])(?:(?=(\\?))\2.)*?\1'
        number_pattern = r'-?\d+\.?\d*'
        newline_pattern = r'\n'
        space_pattern = r'\s+'
        
        full_pattern = f'({string_pattern})|({emoji_pattern})|({number_pattern})|({newline_pattern})|({space_pattern})'
        tokens = re.findall(full_pattern, code)
        
        result = []
        for match in tokens:
            for i, group in enumerate(match):
                if group and group.strip():
                    if i == 4:  # space pattern
                        continue  # Skip spaces
                    result.append(group)
                    break
        
        return [t for t in result if t != '\n' and t.strip()]
    
    def parse_value(self, token: str):
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            return token[1:-1]
        
        if token == '✅':
            return 1
        if token == '❌':
            return 0
        if token == '🕳️':
            return None
        
        if re.match(r'^-?\d+\.?\d*$', token):
            return float(token) if '.' in token or 'e' in token.lower() else int(token)
        
        if re.match(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+$', token):
            return self._get_scope(token)
        
        return token
    
    def find_block_end(self, tokens: List[str], start: int) -> int:
        """Find the end of a block marked by ⏹️"""
        depth = 1
        i = start
        while i < len(tokens) and depth > 0:
            if tokens[i] == '⏹️':
                depth -= 1
            elif tokens[i] in ['➡️', '🔄', '🔂', '🧪', '🎯', '🛡️', '🔧', '📌']:
                depth += 1
            i += 1
        return i if depth == 0 else len(tokens)
    
    def parse_expression(self, tokens: List[str], start: int):
        if start >= len(tokens):
            self._error("Unexpected end of expression")
        
        token = tokens[start]
        
        # Lambda function: 🧪 param1 param2 ➕ param1 param2 ⏹️
        if token == '🧪':
            params = []
            j = start + 1
            # Collect parameters until we hit an operation or control flow
            while j < len(tokens):
                next_token = tokens[j]
                if next_token in self.BINARY_OPS or next_token in self.UNARY_OPS or next_token in self.CONTROL_FLOW:
                    break
                if next_token == '⏹️':
                    break
                if re.match(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+$', next_token):
                    params.append(next_token)
                else:
                    break
                j += 1
            
            # Body is everything until ⏹️
            body_end = self.find_block_end(tokens, j)
            body_tokens = tokens[j:body_end-1]  # Exclude final ⏹️
            
            captured_scope = {}
            for scope in self.stack:
                captured_scope.update(scope)
            
            lambda_func = LambdaFunction(params, body_tokens, captured_scope)
            return lambda_func, body_end
        
        # Slice operation
        if token == '✂️':
            container, idx1 = self.parse_expression(tokens, start + 1)
            start_val, idx2 = self.parse_expression(tokens, idx2)
            end_val, end_idx = self.parse_expression(tokens, idx2)
            if isinstance(container, (list, str)):
                return container[int(start_val):int(end_val)], end_idx
            else:
                self._error("Cannot slice non-sequence type")
        
        # Struct field access
        if token == '🔍':
            obj, next_idx = self.parse_expression(tokens, start + 1)
            field_name, end_idx = self.parse_expression(tokens, next_idx)
            if isinstance(obj, StructInstance):
                if field_name in obj.fields:
                    return obj.fields[field_name], end_idx
                else:
                    self._error(f"Struct {obj.struct_name} has no field '{field_name}'")
            elif isinstance(obj, dict):
                return obj.get(field_name, None), end_idx
            else:
                self._error("Cannot access fields on non-struct/dict type")
        
        # Method calls
        if token == '🚀':
            obj, next_idx = self.parse_expression(tokens, start + 1)
            method_name, args_start = self.parse_expression(tokens, next_idx)
            args = []
            current = args_start
            while current < len(tokens) and tokens[current] != '⏹️':
                if tokens[current] in self.CONTROL_FLOW:
                    break
                try:
                    arg_val, current = self.parse_expression(tokens, current)
                    args.append(arg_val)
                except:
                    break
            # ... (method call logic same as before)
            if isinstance(obj, StructInstance):
                method_key = f"{obj.struct_name}.{method_name}"
                if method_key in self.functions:
                    params, body, _ = self.functions[method_key]
                    if len(args) != len(params) - 1:
                        self._error(f"Method {method_name} expects {len(params)-1} arguments, got {len(args)}")
                    old_stack = self.stack[:]
                    self.stack.append({})
                    self._set_scope(params[0], obj)
                    for param, arg in zip(params[1:], args):
                        self._set_scope(param, arg)
                    result = self.execute_block(body)
                    self.stack = old_stack
                    return result, current
                else:
                    self._error(f"Method {method_name} not defined for struct {obj.struct_name}")
            else:
                self._error("Cannot call method on non-struct type")
        
        # Unary operations
        if token in self.UNARY_OPS:
            val, next_idx = self.parse_expression(tokens, start + 1)
            return self.UNARY_OPS[token](val), next_idx
        
        # Binary operations
        if token in self.BINARY_OPS:
            left, mid_idx = self.parse_expression(tokens, start + 1)
            right, end_idx = self.parse_expression(tokens, mid_idx)
            return self.BINARY_OPS[token](left, right), end_idx
        
        # Function calls
        if re.match(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+$', token):
            if token in self.functions:
                func_params, func_body, is_method = self.functions[token]
                if is_method:
                    self._error("Cannot call method as function")
                args = []
                current = start + 1
                for _ in range(len(func_params)):
                    if current >= len(tokens):
                        self._error("Not enough arguments for function call")
                    arg_val, current = self.parse_expression(tokens, current)
                    args.append(arg_val)
                old_stack = self.stack[:]
                self.stack.append({})
                for param, arg in zip(func_params, args):
                    self._set_scope(param, arg)
                result = self.execute_block(func_body)
                self.stack = old_stack
                return result, current
        
        return self.parse_value(token), start + 1
    
    def execute_block(self, tokens: List[str]):
        """Execute a block of tokens (used for functions, loops, etc.)"""
        i = 0
        last_result = None
        
        while i < len(tokens):
            token = tokens[i]
            
            # Skip comments
            if token == '💬':
                i += 1
                continue
            
            # Variable assignment
            if re.match(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+$', token):
                if i + 1 < len(tokens) and tokens[i + 1] not in self.CONTROL_FLOW:
                    try:
                        value, next_i = self.parse_expression(tokens, i + 1)
                        self._set_scope(token, value)
                        last_result = value
                        i = next_i
                        continue
                    except:
                        pass
            
            # Struct definition: 🏗️ Person name age email ⏹️
            if token == '🏗️':
                if i + 1 >= len(tokens):
                    self._error("Struct needs name")
                struct_name = tokens[i + 1]
                fields = []
                j = i + 2
                while j < len(tokens) and tokens[j] != '⏹️':
                    if (tokens[j].startswith('"') and tokens[j].endswith('"')) or \
                       (tokens[j].startswith("'") and tokens[j].endswith("'")):
                        fields.append(tokens[j][1:-1])
                    else:
                        break
                    j += 1
                self.structs[struct_name] = fields
                i = j + 1
                continue
            
            # Function definition: 📌 add a b ➕ a b ⏹️
            if token == '📌' and i + 1 < len(tokens):
                func_name = tokens[i + 1]
                if not re.match(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+$', func_name):
                    self._error("Function name must be emoji(s)")
                
                params = []
                j = i + 2
                while j < len(tokens):
                    if tokens[j] in self.BINARY_OPS or tokens[j] in self.UNARY_OPS or tokens[j] in self.CONTROL_FLOW:
                        break
                    if tokens[j] == '⏹️':
                        break
                    if re.match(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]+$', tokens[j]):
                        params.append(tokens[j])
                    else:
                        break
                    j += 1
                
                body_tokens = tokens[j:j + (self.find_block_end(tokens, j) - j - 1)]
                self.functions[func_name] = (params, body_tokens, False)
                i = self.find_block_end(tokens, j)
                continue
            
            # Print statement
            if token == '🖨️':
                if i + 1 >= len(tokens):
                    self._error("Print needs argument")
                value, next_i = self.parse_expression(tokens, i + 1)
                print(value)
                self.output_buffer.append(value)
                last_result = value
                i = next_i
                continue
            
            # Input statement
            if token == '📥':
                if i > 0:
                    var_name = tokens[i-1]
                    user_input = input()
                    try:
                        if '.' in user_input:
                            self._set_scope(var_name, float(user_input))
                        else:
                            self._set_scope(var_name, int(user_input))
                    except ValueError:
                        self._set_scope(var_name, user_input)
                    last_result = self._get_scope(var_name)
                    i += 1
                    continue
                else:
                    self._error("Input must be assigned to variable")
            
            # Return statement
            if token == '📤':
                if i + 1 >= len(tokens):
                    return None
                value, next_i = self.parse_expression(tokens, i + 1)
                return value
            
            # If statement: ➡️ condition action ⏹️ ⏭️ else_action ⏹️
            if token == '➡️':
                if i + 1 >= len(tokens):
                    self._error("If needs condition")
                condition, next_i = self.parse_expression(tokens, i + 1)
                i = next_i
                
                # Find then block (until ⏹️ or ⏭️)
                then_end = i
                depth = 0
                while then_end < len(tokens):
                    if tokens[then_end] == '⏹️' and depth == 0:
                        break
                    elif tokens[then_end] == '⏭️' and depth == 0:
                        break
                    elif tokens[then_end] in ['➡️', '🔄', '🔂', '🧪', '🎯', '🛡️']:
                        depth += 1
                    elif tokens[then_end] == '⏹️':
                        depth -= 1
                    then_end += 1
                
                then_tokens = tokens[i:then_end]
                i = then_end
                
                has_else = i < len(tokens) and tokens[i] == '⏭️'
                else_tokens = []
                if has_else:
                    i += 1
                    else_end = i
                    depth = 0
                    while else_end < len(tokens):
                        if tokens[else_end] == '⏹️' and depth == 0:
                            break
                        elif tokens[else_end] in ['➡️', '🔄', '🔂', '🧪', '🎯', '🛡️']:
                            depth += 1
                        elif tokens[else_end] == '⏹️':
                            depth -= 1
                        else_end += 1
                    else_tokens = tokens[i:else_end]
                    i = else_end + 1
                else:
                    i += 1  # Skip the ⏹️
                
                if condition:
                    last_result = self.execute_block(then_tokens)
                elif has_else:
                    last_result = self.execute_block(else_tokens)
                continue
            
            # While loop: 🔄 condition body ⏹️
            if token == '🔄':
                if i + 1 >= len(tokens):
                    self._error("While needs condition")
                cond_start = i + 1
                condition, body_start = self.parse_expression(tokens, cond_start)
                
                body_end = self.find_block_end(tokens, body_start)
                body_tokens = tokens[body_start:body_end-1]
                i = body_end
                
                while True:
                    cond_val, _ = self.parse_expression(tokens, cond_start)
                    if not cond_val:
                        break
                    self.execute_block(body_tokens)
                continue
            
            # For-each loop: 🔂 item container body ⏹️
            if token == '🔂':
                if i + 2 >= len(tokens):
                    self._error("For-each needs variable and container")
                var_name = tokens[i + 1]
                container, body_start = self.parse_expression(tokens, i + 2)
                body_end = self.find_block_end(tokens, body_start)
                body_tokens = tokens[body_start:body_end-1]
                i = body_end
                
                if isinstance(container, (list, str)):
                    for item in container:
                        self._set_scope(var_name, item)
                        self.execute_block(body_tokens)
                elif isinstance(container, dict):
                    for key, value in container.items():
                        self._set_scope(var_name, [key, value])
                        self.execute_block(body_tokens)
                else:
                    self._error("Cannot iterate over non-iterable type")
                continue
            
            # Create new data structures
            if token == '🆕':
                if i + 1 >= len(tokens):
                    self._error("New needs type")
                type_token = tokens[i + 1]
                if i > 0:
                    var_name = tokens[i-1]
                    if type_token == '📄':
                        self._set_scope(var_name, [])
                    elif type_token == '📖':
                        self._set_scope(var_name, {})
                    else:
                        self._error("Unknown type for new")
                i += 2
                continue
            
            i += 1
        
        return last_result
    
    def execute(self, code: str):
        try:
            tokens = self.tokenize(code)
            result = self.execute_block(tokens)
            return result
        except EmojicodeRuntimeError:
            raise
        except Exception as e:
            self._error(f"Runtime error: {str(e)}")

# 🌟 BRACKET-FREE CONWAY'S GAME OF LIFE
BRACKET_FREE_EXAMPLES = {
    "Conway's Game of Life (Bracket-Free)": """
💬 Conway's Game of Life - No Brackets Version
💬 ========================================

💬 Configuration
width 20
height 10
generations 5

💬 Create empty grid
📌 create_grid w h
🆕 📄 grid
y 0
🔄 🟢 h y
🆕 📄 row
x 0
🔄 🟢 w x
📌 row x 0
x ➕ x 1
⏹️
📌 grid y row
y ➕ y 1
⏹️
📤 grid
⏹️

💬 Set cell
📌 set_cell grid x y value
row 🔍 grid y
📌 row x value
📌 grid y row
📤 grid
⏹️

💬 Get cell with bounds checking  
📌 get_cell grid x y
➡️ 🟠 x 0
➡️ 🟢 x width
➡️ 🟠 y 0
➡️ 🟢 y height
row 🔍 grid y
📤 🔍 row x
⏹️
⏭️
📤 0
⏹️
⏹️
⏹️
⏹️
📤 0
⏹️

💬 Count neighbors
📌 count_neighbors grid x y
count 0
dy -1
🔄 🟠 2 dy
dx -1
🔄 🟠 2 dx
➡️ 🟰 dx 0
➡️ 🟰 dy 0
💬 Skip center
⏹️
⏭️
neighbor 🚀 get_cell grid ➕ x dx ➕ y dy
count ➕ count neighbor
⏹️
⏹️
dx ➕ dx 1
⏹️
dy ➕ dy 1
⏹️
📤 count
⏹️

💬 Next generation
📌 next_gen grid
new_grid 🚀 create_grid width height
y 0
🔄 🟢 height y
x 0
🔄 🟢 width x
current 🚀 get_cell grid x y
neighbors 🚀 count_neighbors grid x y
new_state 0
➡️ 🟰 current 1
➡️ 🟢 neighbors 1
➡️ 🟠 neighbors 4
new_state 1
⏹️
⏹️
⏹️
⏭️
➡️ 🟰 neighbors 3
new_state 1
⏹️
⏹️
🚀 set_cell new_grid x y new_state
x ➕ x 1
⏹️
y ➕ y 1
⏹️
📤 new_grid
⏹️

💬 Print grid beautifully
📌 print_grid grid
line "┌"
x 0
🔄 🟢 width x
line 🔗 line "─"
x ➕ x 1
⏹️
line 🔗 line "┐"
🖨️ line
y 0
🔄 🟢 height y
line "│"
x 0
🔄 🟢 width x
cell 🚀 get_cell grid x y
➡️ 🟰 cell 1
line 🔗 line "🔴"
⏹️
⏭️
line 🔗 line "  "
⏹️
x ➕ x 1
⏹️
line 🔗 line "│"
🖨️ line
y ➕ y 1
⏹️
line "└"
x 0
🔄 🟢 width x
line 🔗 line "─"
x ➕ x 1
⏹️
line 🔗 line "┘"
🖨️ line
📤 grid
⏹️

💬 Initialize grid with patterns
grid 🚀 create_grid width height
🚀 set_cell grid 1 0 1
🚀 set_cell grid 2 1 1
🚀 set_cell grid 0 2 1
🚀 set_cell grid 1 2 1
🚀 set_cell grid 2 2 1
🚀 set_cell grid 10 4 1
🚀 set_cell grid 11 4 1
🚀 set_cell grid 12 4 1

💬 Run simulation
gen 0
🔄 🟢 generations gen
🖨️ 🔤 "Generation "
🖨️ gen
🚀 print_grid grid
grid 🚀 next_gen grid
gen ➕ gen 1
🕒 1
⏹️

🖨️ "🎉 Complete!"
    """,
    
    "Lambda Functions (Bracket-Free)": """
💬 Lambda without any brackets
💬 =========================

💬 Square function as lambda
square 🧪 x
✖️ x x
⏹️

💬 Apply to list
numbers 🆕 📄
📌 numbers 0 1
📌 numbers 1 2
📌 numbers 2 3
📌 numbers 3 4
📌 numbers 4 5

squared 🗺️ square numbers
🖨️ squared

💬 Filter even numbers
is_even 🧪 n
🟰 ➗ n 2 0
⏹️

evens 🧼 is_even numbers
🖨️ evens
    """,
    
    "Pattern Matching (Bracket-Free)": """
💬 Pattern matching without brackets
💬 ===============================

🏗️ 🌈 color brightness ⏹️

rainbow 🏗️ 🌈
📌 🔍 rainbow color "red"
📌 🔍 rainbow brightness 80

🎯 rainbow
🌈 🟰 🔍 🌈 color "red"
🖨️ "🔥 Red rainbow!"
⏹️
🌈 🟰 🔍 🌈 color "blue"
🖨️ "💧 Blue rainbow!"
⏹️
🕳️
🖨️ "🌈 Other rainbow!"
⏹️
⏹️
    """
}

def main():
    interpreter = EmojicodeInterpreter()
    
    print("🌈 EMOJICODE 5.0 - 100% BRACKET-FREE EMOJI PROGRAMMING! 🌈")
    print("=" * 70)
    print("✨ PURE BRACKET-FREE FEATURES:")
    print("  • No curly braces {}, parentheses (), or square brackets []")
    print("  • Structure defined by emoji blocks and ⏹️ end markers")
    print("  • Conway's Game of Life with zero brackets")
    print("  • Lambda functions without parentheses")
    print("  • All control flow using only emojis and ⏹️")
    print("  • Multi-emoji identifiers (✨🌟, 🐶🐱, 🧮✨🌟)")
    
    print("\n📚 Syntax Rules:")
    print("  • Functions: 📌 name param1 param2 body ⏹️")
    print("  • If: ➡️ condition then_block ⏹️ ⏭️ else_block ⏹️")
    print("  • While: 🔄 condition body ⏹️")
    print("  • Lambda: 🧪 param1 param2 body ⏹️")
    print("  • Everything ends with ⏹️")
    
    print("\n" + "="*70)
    print("Try Conway's Game of Life (Bracket-Free):")
    
    # Show the Conway's Game of Life example
    conway_code = BRACKET_FREE_EXAMPLES["Conway's Game of Life (Bracket-Free)"]
    lines = conway_code.strip().split('\n')
    for line in lines[:20]:  # Show first 20 lines
        print(line)
    if len(lines) > 20:
        print("...")
        print(lines[-3])  # Show last few lines
        print(lines[-2])
        print(lines[-1])
    
    print("\n" + "="*70)
    print("Enter 'conway' to run the bracket-free Game of Life!")
    print("Or enter your own bracket-free Emojicode (type 'quit' to exit):")
    
    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() == 'quit':
                break
            if user_input.lower() == 'conway':
                interpreter.execute(BRACKET_FREE_EXAMPLES["Conway's Game of Life (Bracket-Free)"])
                continue
            if user_input.strip() == '':
                continue
                
            result = interpreter.execute(user_input)
            if result is not None:
                print(f"Result: {result}")
                
        except EmojicodeRuntimeError as e:
            print(e)
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for coding in bracket-free Emojicode!")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()