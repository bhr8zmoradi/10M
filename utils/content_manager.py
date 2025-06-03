import json
import hashlib

class ContentManager:
    def __init__(self):
        self.cache = {}
        self.last_hash = ""
    
    def load_content(self, file_path):
        current_hash = self._calculate_hash(file_path)
        
        if current_hash != self.last_hash:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
            self.last_hash = current_hash
        
        return self.cache
    
    def _calculate_hash(self, file_path):
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
