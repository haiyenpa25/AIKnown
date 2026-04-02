from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_php
import tree_sitter_javascript
import os

class CodeParser:
    def __init__(self):
        # Load languages using the tree-sitter 0.22+ API pattern
        self.langs = {
            'python': Language(tree_sitter_python.language()),
            'php': Language(tree_sitter_php.language_php()),
            'javascript': Language(tree_sitter_javascript.language())
        }
        self.parser = Parser()

    def determine_language(self, path):
        if path.endswith('.py'): return 'python'
        elif path.endswith('.php'): return 'php'
        elif path.endswith(('.js', '.ts')): return 'javascript' # For MVP use js parser for ts roughly
        return None

    def parse_file(self, full_path):
        lang_name = self.determine_language(full_path)
        if not lang_name: return None, []
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content_bytes = bytes(content, 'utf8')
        except Exception:
            return lang_name, []

        self.parser.language = self.langs[lang_name]
        b_tree = self.parser.parse(content_bytes)
        
        symbols = []
        if lang_name == 'python':
            symbols = self._parse_python(b_tree, content_bytes)
        elif lang_name == 'php':
            symbols = self._parse_php(b_tree, content_bytes)
        elif lang_name == 'javascript':
            symbols = self._parse_js(b_tree, content_bytes)
            
        return lang_name, symbols

    def _parse_python(self, tree, content_bytes):
        symbols = []
        def get_calls(node):
            calls = set()
            def walk(n):
                if n.type == 'call':
                    for c in n.children:
                        if c.type in ['identifier']:
                            calls.add(content_bytes[c.start_byte:c.end_byte].decode('utf-8'))
                        elif c.type == 'attribute':
                            for cc in reversed(c.children):
                                if cc.type == 'identifier':
                                    calls.add(content_bytes[cc.start_byte:cc.end_byte].decode('utf-8'))
                                    break
                for child in n.children:
                    walk(child)
            walk(node)
            return list(calls)

        def traverse(node, current_class=""):
            if node.type in ['import_statement', 'import_from_statement']:
                for child in node.children:
                    if child.type == 'dotted_name':
                        mod_name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        symbols.append({
                            'name': mod_name,
                            'type': 'External',
                            'signature': '',
                            'docstring': '',
                            'dependencies': []
                        })
                        
            if node.type in ['function_definition', 'class_definition']:
                raw_name = ""
                for child in node.children:
                    if child.type == 'identifier':
                        raw_name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        name = f"{current_class}.{raw_name}" if (current_class and node.type == 'function_definition') else raw_name
                        type_ = 'Class' if node.type == 'class_definition' else 'Function'
                        deps = get_calls(node) if type_ == 'Function' else []
                        symbols.append({
                            'name': name,
                            'type': type_,
                            'signature': name + '()',
                            'docstring': '',
                            'dependencies': deps
                        })
                        break
                
                pass_class = raw_name if node.type == 'class_definition' else current_class
                for child in node.children:
                    traverse(child, pass_class)
            else:
                for child in node.children:
                    traverse(child, current_class)
        traverse(tree.root_node)
        return symbols

    def _parse_php(self, tree, content_bytes):
        symbols = []
        def get_calls(node):
            calls = set()
            def walk(n):
                if n.type in ['function_call_expression', 'method_call_expression']:
                    for c in n.children:
                        if c.type == 'name':
                            calls.add(content_bytes[c.start_byte:c.end_byte].decode('utf-8'))
                for child in n.children:
                    walk(child)
            walk(node)
            return list(calls)

        def traverse(node, current_class=""):
            # PHP namespace use / require
            if node.type in ['use_declaration', 'require_once_expression', 'include_expression']:
                for child in node.children:
                    if child.type in ['name', 'string']:
                        mod_name = content_bytes[child.start_byte:child.end_byte].decode('utf-8').strip("\"'")
                        symbols.append({'name': mod_name, 'type': 'External', 'signature': '', 'docstring': '', 'dependencies': []})

            if node.type in ['function_definition', 'method_declaration', 'class_declaration']:
                raw_name = ""
                for child in node.children:
                    if child.type == 'name':
                        raw_name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        name = f"{current_class}::{raw_name}" if (current_class and node.type == 'method_declaration') else raw_name
                        type_ = 'Class' if node.type == 'class_declaration' else 'Function'
                        deps = get_calls(node) if type_ == 'Function' else []
                        symbols.append({
                            'name': name,
                            'type': type_,
                            'signature': name + '()',
                            'docstring': '',
                            'dependencies': deps
                        })
                        break
                pass_class = raw_name if node.type == 'class_declaration' else current_class
                for child in node.children:
                    traverse(child, pass_class)
            else:
                for child in node.children:
                    traverse(child, current_class)
        traverse(tree.root_node)
        return symbols

    def _parse_js(self, tree, content_bytes):
        symbols = []
        def get_calls(node):
            calls = set()
            def walk(n):
                if n.type == 'call_expression':
                    for c in n.children:
                        if c.type == 'identifier':
                            calls.add(content_bytes[c.start_byte:c.end_byte].decode('utf-8'))
                        elif c.type == 'member_expression':
                            for cc in reversed(c.children):
                                if cc.type == 'property_identifier':
                                    calls.add(content_bytes[cc.start_byte:cc.end_byte].decode('utf-8'))
                                    break
                for child in n.children:
                    walk(child)
            walk(node)
            return list(calls)
            
        def traverse(node, current_class=""):
            if node.type in ['import_statement']:
                for child in node.children:
                    if child.type == 'string':
                        mod_name = content_bytes[child.start_byte:child.end_byte].decode('utf-8').strip("\"'")
                        symbols.append({'name': mod_name, 'type': 'External', 'signature': '', 'docstring': '', 'dependencies': []})
            elif node.type == 'call_expression':
                # Catch require('module')
                pass # can implement more deeply later
                
            if node.type in ['function_declaration', 'class_declaration']:
                raw_name = ""
                for child in node.children:
                    if child.type == 'identifier':
                        raw_name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        name = f"{current_class}.{raw_name}" if (current_class and node.type == 'function_declaration') else raw_name
                        type_ = 'Class' if node.type == 'class_declaration' else 'Function'
                        deps = get_calls(node) if type_ == 'Function' else []
                        symbols.append({
                            'name': name,
                            'type': type_,
                            'signature': name + '()',
                            'docstring': '',
                            'dependencies': deps
                        })
                        break
                pass_class = raw_name if node.type == 'class_declaration' else current_class
                for child in node.children:
                    traverse(child, pass_class)
            else:
                for child in node.children:
                    traverse(child, current_class)
        traverse(tree.root_node)
        return symbols
