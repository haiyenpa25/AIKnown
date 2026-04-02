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
        def traverse(node):
            if node.type in ['function_definition', 'class_definition']:
                for child in node.children:
                    if child.type == 'identifier':
                        name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        type_ = 'Class' if node.type == 'class_definition' else 'Function'
                        symbols.append({
                            'name': name,
                            'type': type_,
                            'signature': name + '()',
                            'docstring': ''
                        })
                        break
            for child in node.children:
                traverse(child)
        traverse(tree.root_node)
        return symbols

    def _parse_php(self, tree, content_bytes):
        symbols = []
        def traverse(node):
            if node.type in ['function_definition', 'method_declaration', 'class_declaration']:
                for child in node.children:
                    if child.type == 'name':
                        name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        type_ = 'Class' if node.type == 'class_declaration' else 'Function'
                        symbols.append({
                            'name': name,
                            'type': type_,
                            'signature': name + '()',
                            'docstring': ''
                        })
                        break
            for child in node.children:
                traverse(child)
        traverse(tree.root_node)
        return symbols

    def _parse_js(self, tree, content_bytes):
        symbols = []
        def traverse(node):
            if node.type in ['function_declaration', 'class_declaration']:
                for child in node.children:
                    if child.type == 'identifier':
                        name = content_bytes[child.start_byte:child.end_byte].decode('utf-8')
                        type_ = 'Class' if node.type == 'class_declaration' else 'Function'
                        symbols.append({
                            'name': name,
                            'type': type_,
                            'signature': name + '()',
                            'docstring': ''
                        })
                        break
            for child in node.children:
                traverse(child)
        traverse(tree.root_node)
        return symbols
