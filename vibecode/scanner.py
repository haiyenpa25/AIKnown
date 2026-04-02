import os
import pathspec

class Scanner:
    def __init__(self, root_dir='.'):
        self.root_dir = root_dir
        self.ignore_spec = self._load_gitignore()

    def _load_gitignore(self):
        gitignore_path = os.path.join(self.root_dir, '.gitignore')
        lines = []
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Luôn bỏ qua thư mục .git, .vibecode nội bộ và các thư mục rác phổ biến
        lines.extend(['.git/', '.vibecode/', '__pycache__/', '.venv/', 'node_modules/', 'vendor/'])
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, lines)

    def scan_files(self):
        scanned_files = []
        for root, dirs, files in os.walk(self.root_dir):
            if not root.endswith(('/', '\\')):
                root_path = root + '/'
            else:
                root_path = root
            
            # Lọc dirs để os.walk bỏ qua nhánh không cần thiết (tối ưu tốc độ)
            dirs[:] = [d for d in dirs if not self.ignore_spec.match_file(os.path.relpath(os.path.join(root, d), self.root_dir).replace('\\', '/') + '/')]
            
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.root_dir).replace('\\', '/')
                if not self.ignore_spec.match_file(rel_path):
                    # Giới hạn phân tích trên 1 số đuôi file (Giai đoạn MVP)
                    if rel_path.endswith(('.py', '.php', '.js', '.ts')):
                        full_path = os.path.join(self.root_dir, rel_path)
                        try:
                            last_modified = os.path.getmtime(full_path)
                            scanned_files.append((rel_path, last_modified))
                        except Exception:
                            pass
        return scanned_files
