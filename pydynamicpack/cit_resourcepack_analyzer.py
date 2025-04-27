import os
import re
import json

class CITResourcePackAnalyzer:
    def __init__(self, resourcepack_path):
        self.resourcepack_path: str = resourcepack_path
        self.cit_root_dir = os.path.join(self.resourcepack_path, "assets", "minecraft", "optifine", "cit")
        self.textures_dir = os.path.join(self.resourcepack_path, "assets", "minecraft", "textures")
        self.models_dir = os.path.join(self.resourcepack_path, "assets", "minecraft", "models")
        self.used_files = {}
        self.missing_files = {}
        self.all_files = []


    def _process_json_file(self, parent_dir, json_file):
        """Обрабатывает .json файл и извлекает используемые пути."""
        json_path = os.path.join(parent_dir, json_file)
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_content = json.load(f)
                if 'textures' in json_content:
                    tx = json_content['textures']
                    for key in tx.keys():
                        texture = tx[key]
                        pptexfield = texture if texture.endswith(".png") else texture + ".png"
                        self._process_texture_field(json_path, os.path.dirname(json_path), pptexfield)

        except json.JSONDecodeError as e:
            print(f"Ошибка при чтении JSON файла {json_path}: {e}")

        except Exception as e:
            print(f"Ошибка при обработке JSON файла {json_path}: {e}")

    def _process_model_field(self, ppusedby, parent_dir, field):
        """Обрабатывает путь к файлу, добавляя расширение по умолчанию, если необходимо."""
        #print(f"ppusedby: {ppusedby} parent_dir: {parent_dir} field: {field}")
        field = field.strip()
        if not field:
            return None

        is_path = '/' in field or '\\' in field
        is_has_ext = field.endswith(".json")

        if is_path:
            print("WARN is_path")
        else:
            ppath = os.path.normpath(os.path.join(parent_dir, field + ("" if is_has_ext else ".json")))
            if os.path.exists(ppath):
                self.mark_as_used(ppath, ppusedby)
                self._process_json_file(os.path.dirname(ppath), os.path.basename(ppath))
            else:
                self.mark_as_missing(ppath, ppusedby)

    def _process_texture_field(self, ppusedby, parent_dir, field):
        field = field.strip()
        if field.startswith("./"):
            field = field[2::]
        if not field:
            return None

        is_path = '/' in field or '\\' in field
        is_has_ext = field.endswith(".png")

        if is_path:
            print("WARN is_path")
        else:
            ppath = os.path.normpath(os.path.join(parent_dir, field + ("" if is_has_ext else ".png")))
            if os.path.exists(ppath):
                self.mark_as_used(ppath, ppusedby)
                _e = ppath.replace(".png", "_e.png")
                if os.path.exists(_e):
                    self.mark_as_used(_e, ppath)

                mcmeta = ppath.replace(".png", ".png.mcmeta")
                if os.path.exists(mcmeta):
                    self.mark_as_used(mcmeta, ppath)

                _e_mcmeta = ppath.replace(".png", "_e.png.mcmeta")
                if os.path.exists(_e_mcmeta):
                    self.mark_as_used(_e_mcmeta, ppath)

            else:
                self.mark_as_missing(ppath, ppusedby)

    def _process_properties_file(self, root, file):
        """Обрабатывает .properties файл и извлекает используемые пути."""
        properties_path = os.path.join(root, file)
        try:
            with open(properties_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    model_matches = re.findall(r"model(\..*)?=(.*)", line)
                    for match in model_matches:
                        self._process_model_field(properties_path, os.path.dirname(properties_path), match[1])

                    texture_matches = re.findall(r"texture(\..*)?=(.*)", line)
                    for match in texture_matches:
                        self._process_texture_field(properties_path, os.path.dirname(properties_path), match[1])

            self.mark_as_used(properties_path, "<properties>")
        except Exception as e:
            print(f"Ошибка при обработке файла {properties_path}: {e}")

    def mark_as_used(self, ppath, ppusedby):
        self._mark_as(self.used_files, ppath, ppusedby)

    def mark_as_missing(self, ppath, ppusedby):
        self._mark_as(self.missing_files, ppath, ppusedby)

    def _mark_as(self, _dict, ppath, ppusedby):
        path = os.path.relpath(ppath, self.resourcepack_path)
        usedby = os.path.relpath(ppusedby, self.resourcepack_path) if '<' not in ppusedby else ppusedby
        if path not in _dict:
            _dict[path] = [usedby]

        else:
            if usedby not in _dict[path]:
                _dict[path].append(usedby)

    def analyze(self):
        """Находит неиспользуемые файлы в ресурспаке."""
        if os.path.exists(self.cit_root_dir):
            for root, _, files in os.walk(self.cit_root_dir):
                for file in files:
                    ppath = os.path.join(root, file)
                    self.all_files.append(os.path.relpath(ppath, self.resourcepack_path))
                    if file.endswith(".properties"):
                        self._process_properties_file(root, file)
