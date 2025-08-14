import json
import os

class MemoryStore:
    def __init__(self, profile_id):
        self.file_path = "memories.json"
        self.profile_id = profile_id
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def set(self, key, value):
        if self.profile_id not in self.data:
            self.data[self.profile_id] = {}
        self.data[self.profile_id][key] = value
        self.save()

    def get_all(self):
        return self.data.get(self.profile_id, {})

    def clear(self):
        if self.profile_id in self.data:
            self.data[self.profile_id] = {}
            self.save()
