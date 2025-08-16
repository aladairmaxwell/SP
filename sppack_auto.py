import argparse
import csv
import json
import os.path
import re
import struct
from pydynamicpack.splashes_unwrapper import SplashesUnwrapper

from PIL import Image

DEBUG = False
IGNORE = [
    ".git",
    ".idea",
    "__pycache__",
    ".DS_Store",
    ".gitignore",
    "README.md",
    ".py",
    "packsquash"
]

SPLASHES_BUILDS = [
    {
        "name": "Default splashes",
        "from": "splashes-with-metadata.txt",
        "to": "sp_splashes/assets/minecraft/texts/splashes.txt"
    }
]

MAIN_PATH = "C:/Users/PobiH/Downloads/SP-main"

def get_filepaths(directory):
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath.replace("\\", "/"))  # Add it to the list.

    debug(f"get_filepaths({directory}) return {file_paths}")
    return file_paths  # Self-explanatory.


def enablePrettyPrint():
    rebuildPrettyPrint(True)


def disablePrettyPrint():
    rebuildPrettyPrint(False)


def rebuildPrettyPrint(state: bool):
    for e in get_filepaths(MAIN_PATH):
        isIgn = False
        for ign in IGNORE:
            ign = "./" + ign
            if (e.startswith(ign)):
                isIgn = True

        if (isIgn):
            continue

        if (e.endswith(".json")):
            cool_json = None
            with open(e, "r", encoding='utf-8') as file:
                try:
                    cool_json = json.load(file)

                except Exception as err:
                    print(f"[ERROR] {err} while processing file {e}")

            if (cool_json != None):
                with open(e, "w", encoding='utf-8') as file:
                    if (state):
                        json.dump(cool_json, file, indent=4)

                    else:
                        json.dump(cool_json, file)


def isUpperCase(e: str):
    for x in e:
        if x.isupper():
            return True

    return False


def renameToLower(parent, path, x: str):
    os.renames(parent + x, parent + x.lower())
    print(f"RENAME {parent + x} -> {parent + x.lower()}")


def lowerCaseAll(init_dir):
    for e in get_filepaths(init_dir):
        upper = isUpperCase(e)
        if (upper):
            l = []
            for x in e.split("/"):
                path = "/".join(l) + "/" + x
                parent = "/".join(l) + "/"
                isDir = os.path.isdir(path)
                if (isDir and isUpperCase(x)):
                    renameToLower(parent, path, x)

                l.append(x)


def update_contents_csv():
    dirs = open("content_directories.txt", "r", encoding='utf-8').read().split("\n")
    with open("contents.csv", 'w', newline='\n', encoding='utf-8') as csvfile:
        csv_writter = csv.writer(csvfile, delimiter=',',
                                 quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writter.writerow(["id", "work_dir", "files_list", "files_list_hash"])
        for dir in dirs:
            #with open(dir + "/files.csv", 'rb', encoding='utf-8') as open_file:
            #    content = open_file.read()
            csv_writter.writerow([dir.replace("/", "_"), dir, dir + "/files.csv", "ff00ffffffffffffffffffffffff"])


def debug(m):
    if DEBUG:
        print(f"DEBUG: {m}")


def analyze():
    for path in get_filepaths(MAIN_PATH):
        if re.search("[^a-z1-90_\\-./]", path) != None:
            print(path)


def fixPng_resize(path, nx, ny):
    # Open the original image
    original_image = Image.open(path)
    original_image = original_image.resize((nx, ny), Image.NEAREST)
    # Save the result
    original_image.save(path)
    print(f"[Modify] Resized image in {nx}, {ny} {path}")


def findBadPngResolution():
    for path in get_filepaths(MAIN_PATH):
        if (path.endswith(".png")):
            #print(f"PNG FOUND {path}")
            try:
                with open(path, 'rb') as f:
                    data = f.read()

                size = get_image_info(data)
                x = size[0]
                y = size[1]

                size_modify = 1

                if x % 16 == 0 and y % 16 == 0:
                    continue

                print(f"Bad png {size} at {path}")

                while x*size_modify % 16 != 0 or y*size_modify % 16 != 0:
                    size_modify += 1

                fixPng_resize(path, fix_png_dim(x*size_modify), fix_png_dim(y*size_modify))

            except Exception as e:
                print(f"PNG AT {path}: {e}")

def get_image_info(data):
    if True:
        w, h = struct.unpack('>LL', data[16:24])
        width = int(w)
        height = int(h)
    else:
        raise Exception('not a png image')
    return width, height


def fix_png_dim(dim):
    d = dim % 16
    if d == 0:
        return dim

    return dim + (16 - d)


CIT_KEY_NAME = "components.custom_name"
CIT_KEY_LORE = "components.lore"
CIT_KEY_OTHER = "components."
CIT_KEY_POTION = "components.potion_contents.potion"
CIT_KEY_MODEL_BOW = "model"
CIT_KEY_RESOLVED = "components.written_book_content.resolved"
CIT_KEY_VARIANT = "components.bucket_entity_data.Variant"
CIT_KEY_TITLE = "components.written_book_content.title"

stat = {
    "merged_to_components": {
        "lore": 0,
        "name": 0,
        "potion": 0,
        "resolved": 0,
        "title" : 0,
        "variant": 0,
        "other": 0,
        "model_fix": 0,
        "remove_minecraft_namespace": 0,
        "writings_on_disk": 0
    },
    "total_properties": 0,
    "total_renames": 0
}

def processPropertiesFile(renamesFile, e):
    print(e)
    modified = []
    stat["total_properties"] += 1
    with open(e, 'r', newline='\n', encoding='utf-8') as propFile:
        prop_content = propFile.read()
        if "nbt.display.Name=" in prop_content:
            prop_content = prop_content.replace("nbt.display.Name=", f"{CIT_KEY_NAME}=")
            modified.append(f"nbt.display.Name -> {CIT_KEY_NAME}")
            stat["merged_to_components"]["name"] += 1

        if "nbt.display.Lore" in prop_content:
            prop_content = prop_content.replace("nbt.display.Lore", f"{CIT_KEY_LORE}")
            modified.append(f"replace 'nbt.display.Lore' -> {CIT_KEY_LORE}")
            stat["merged_to_components"]["lore"] += 1

        if "nbt.resolved" in prop_content:
            prop_content = prop_content.replace("nbt.resolved", f"{CIT_KEY_RESOLVED}")
            modified.append(f"replace 'nbt.resolved' -> {CIT_KEY_RESOLVED}")
            stat["merged_to_components"]["resolved"] += 1

        if "nbt.Variant" in prop_content:
            prop_content = prop_content.replace("nbt.Variant", f"{CIT_KEY_VARIANT}")
            modified.append(f"replace 'nbt.Variant' -> {CIT_KEY_VARIANT}")
            stat["merged_to_components"]["variant"] += 1

        if "nbt.Potion" in prop_content:
            prop_content = prop_content.replace("nbt.Potion", f"{CIT_KEY_POTION}")
            modified.append(f"replace 'nbt.Potion' -> {CIT_KEY_POTION}")
            stat["merged_to_components"]["potion"] += 1
            
        if "nbt.title" in prop_content:
            prop_content = prop_content.replace("nbt.title", f"{CIT_KEY_TITLE}")
            modified.append(f"replace 'nbt.title' -> {CIT_KEY_TITLE}")
            stat["merged_to_components"]["title"] += 1

        if "nbt." in prop_content:
            prop_content = prop_content.replace("nbt.", f"{CIT_KEY_OTHER}")
            modified.append(f"replace 'nbt.' -> {CIT_KEY_OTHER}")
            stat["merged_to_components"]["other"] += 1

        if "model.bow_standby" in prop_content:
            prop_content = prop_content.replace("model.bow_standby", f"{CIT_KEY_MODEL_BOW}")
            modified.append(f"replace 'model.bow_standby' -> {CIT_KEY_MODEL_BOW}")
            stat["merged_to_components"]["model_fix"] += 1

        if "crossbow_standby" in prop_content:
            prop_content = prop_content.replace("crossbow_standby", f"{CIT_KEY_MODEL_BOW}")
            modified.append(f"replace 'crossbow_standby' -> {CIT_KEY_MODEL_BOW}")
            stat["merged_to_components"]["model_fix"] += 1

        if "components.minecraft\\:custom_name=" in prop_content:
            prop_content = prop_content.replace("components.minecraft\\:custom_name=", f"{CIT_KEY_NAME}=")
            modified.append(f"remove unnecessary minecraft namespace 'components.minecraft\\:custom_name' -> {CIT_KEY_LORE}")
            stat["merged_to_components"]["remove_minecraft_namespace"] += 1

        lines = []
        for x in prop_content.split("\n"):
            if len(x.strip()) != 0:
                if (not x.strip().startswith("#")):
                    lines.append(x.strip())

        l = [line.split("=") for line in lines]
        d = {r[0].strip(): r[1].strip() for r in l}

        if CIT_KEY_NAME in d.keys():
            if "matchItems" in d:
                items = d["matchItems"]
            else:
                items = "nothing"

            value = d[CIT_KEY_NAME].encode('raw_unicode_escape').decode('unicode_escape').replace("\"", "\"\"")
            renamesFile.write(f"\"{value}\",{items},{e[2::]}\n")
            stat["total_renames"] += 1

    if len(modified) > 0:
        print(f"Writing modified file: {modified}")
        with open(e, 'w', newline='\n', encoding='utf-8') as propFile:
            propFile.write(prop_content)
            stat["merged_to_components"]["writings_on_disk"] += 1


def upgradeToComponentAndRenames():
    with open("renames.csv", 'w', newline='\n', encoding='utf-8') as renamesFile:
        for e in get_filepaths(MAIN_PATH):
            if e.endswith(".properties") and "packsquash" not in e:
                processPropertiesFile(renamesFile, e)

    print("== STAT ==")
    print(json.dumps(stat, indent=2))


def splashesbuild():
    sw = SplashesUnwrapper(DEBUG)
    for s in SPLASHES_BUILDS:
        print(f"Build splashes: {s['name']}")
        sw.wrapped_file_to_unwrapped(s["from"], s["to"])


def run():
    parser = argparse.ArgumentParser(description='SP Pack')
    parser.add_argument('--mode', type=str, default="no_default", help='Automatically mode')
    cmd = parser.parse_args().mode

    print("SPPack automatization tool")
    print("")
    print("Select a hook")
    print("[1] pretty-print optimize")
    print("[2] lowercase all dirs")
    print("[3] analyze")
    print("[4] update_contents_csv")
    print("[5] find all png with size % 16 != 0")
    print("[6] Fix NBT -> Component && update renames.txt")
    print("[7] splashes build")

    if cmd == "no_default":
        cmd = input(" ---> ")

    print(f"Mode: {cmd}")
    if (cmd == "1"):
        i = input("[E]nable or [D]isable pretty print?\n ->> ")
        if i.lower() == "e":
            enablePrettyPrint()


        elif (i.lower() == "d"):
            disablePrettyPrint()

        else:
            print("failed to recognize command")

    if (cmd == "2"):
        print("Lowercase all dirs in ..optifine/cit")
        lowerCaseAll(input("Init dir -> ") + "/assets/minecraft/optifine/cit")

    if cmd == "3":
        print("Analyzing...")
        analyze()

    if cmd == "4":
        update_contents_csv()

    if cmd == "5":
        findBadPngResolution()

    if cmd == "6":
        upgradeToComponentAndRenames()

    if cmd == "7":
        splashesbuild()


if __name__ == "__main__":
    run()
