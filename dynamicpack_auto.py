# Script for automatize creating DynamicPack mod dynamic_repo
# Modrinth: https://modrinth.com/mod/dynamicpack
# Mod GitHub: https://github.com/AdamCalculator/DynamicPack
# Author: AdamCalculator
#
DVER = 7
DDEBUG = False
#


import argparse
parser = argparse.ArgumentParser(description='DynamicPack')
parser.add_argument('--mode', type=str, default="no_default", help='Automatically mode')
args = parser.parse_args()


import json
import os
import hashlib
from pathlib import Path


jrepo = None      # dynamicmcpack.repo.json content
contents = {}
EXCLUDE_UNASSIGNED = [
    "dynamicmcpack.repo.json",
    "dynamicmcpack.repo.json.sig",
    "dynamicmcpack.repo.build"
]
files_registered = []
convert_line_ending_rules = {
    ".png": False,
    ".jpg": False,
    ".jpeg": False,
    ".txt": True,
    ".mcmeta": True,
    ".json": True,
    ".jem": True,
    ".properties": True,
    ".fsh": True,
    ".vsh": True,
    ".lang": True,
    ".DS_Store": False
}


def main():
    print("Welcome DynamicPack mod aromatization script!")
    print(f"Version v{DVER}")
    print("")
    init_repo()

    print("Enter action")
    print(" [1] resync-all")
    print("  \\ Sync all contents with filesystem")
    print("  \\ and recalculate hashes")
    print(" [2] Prepare to publish update - Increment build number and recalculate hashes")
    print("")
    print(" [3] Add new content - create new content and init this")
    print(" [4] Sync content with filesystem")
    print("  \\ Sync selected content with filesystem")
    print(" [5] Re-calculate hashes of exist added to contents files")
    print(" [6] Find no added to contents files")

    if (args.mode == "no_default"):
        act = input("\t\t-> ")

    else:
        act = args.mode
        print("Automatically mode parsed from args: " + act)

    if act == "1":
        for x in contents:
            remake_content(x, ask_subdir=False)

        recalculate_hashes()
        print("Done!")

    if act == "2":
        b = jrepo["build"] + 1
        jrepo["build"] = b;
        with open("dynamicmcpack.repo.build", "w") as open_file:
            open_file.write(str(b))

        save_jrepo()
        print(f"Done! build={b}\n[!] Don't forget sign dynamicmcpack.repo.json again if you using signature & verifying")

    if act == "3":
        add_new_content()
        print("Done!")

    if act == "4":
        print("Select content file for update")
        file = input_exists_content_file()
        b = input("Use saved parent parameter for scan-subdirectory?\n\t\t [Y/n] -> ").lower() == "y"
        remake_content(file, ask_subdir=not b)
        print("Done!")

    if act == "5":
        recalculate_hashes()
        print("Done!")

    if act == "6":
        dir = input("Directory for check -> ")
        for e in get_filepaths("./"):
            e = e[2::]
            if not e.startswith(dir):
                continue

            if e.startswith(".git/"):
                continue

            if e.startswith(".idea/"):
                continue

            if e == ".gitignore":
                continue

            if not (e in files_registered):
                if not _is_system_file(e):
                    print(f"Found unassigned file: {e}")


def init_repo():
    global contents, jrepo
    contents = {}
    jrepo = json.loads(open("dynamicmcpack.repo.json", "r").read())
    debug("Repo file loaded!")
    for x in jrepo["contents"]:
        EXCLUDE_UNASSIGNED.append(x["url"])
        contents[x["url"]] = json.loads(open(x["url"], "r").read())
        cont = contents[x["url"]]["content"]
        for file in cont["files"]:
            files_registered.append(_path_repair_1(cont["remote_parent"], cont["parent"], file))

    debug(f"contents = {contents}")


def save_jrepo():
    global jrepo
    open("dynamicmcpack.repo.json", "w").write(json.dumps(jrepo, indent='\t'))
    calc_sha1_hash("dynamicmcpack.repo.json")



def add_new_content():
    directory = input("Directory for content -> ")

    cloc = input(f"Content file location\n [1] - in root of repo\n [2] - in directory '{directory}'\n\t\t-> ")
    filename = input(f"content.json filename -> ")
    os.makedirs(directory, exist_ok=True)

    if cloc == "1":
        file = filename
    elif cloc == "2":
        file = directory + "/" + filename
    else:
        print("Not valid")
        return

    j = {
        "url": file,
        "hash": "-hash-not-generated-",
        "id": input("Enter Content ID\n\t\t -> ")
    }
    jrepo["contents"].append(j)

    contents[file] = {
        "formatVersion": 1,
        "content": {
            "parent": "",
            "remote_parent": directory,
            "files": {}
        }
    }
    open(file, "w").write(json.dumps(contents[file], indent='\t'))
    calc_sha1_hash(file)
    save_jrepo()
    print(f"Content file added to repo with not calculated hash and created at {file}")


def recalculate_hashes():
    for x in contents:
        parent = contents[x]["content"]["parent"]
        remPar = contents[x]["content"]["remote_parent"]
        files = contents[x]["content"]["files"]
        for filePath in files:
            globalFilePath = remPar + "/" + parent + "/" + filePath
            if len(parent) == 0 and len(remPar) == 0:
                globalFilePath = filePath;

            elif len(parent) == 0 and len(remPar) != 0:
                globalFilePath = remPar + "/" + filePath;

            elif len(parent) != 0 and len(remPar) == 0:
                globalFilePath = parent + "/" + filePath;

            fileJson = contents[x]["content"]["files"][filePath]
            fileJson["hash"] = calc_sha1_hash(globalFilePath)
            debug(f"recalculate_hashes: Set hash of {globalFilePath}")
        open(x, "w").write(json.dumps(contents[x], indent='\t'))
        calc_sha1_hash(x)

        # Calculate hash for content.json file and write to repo main file
        i = 0
        for x1 in jrepo["contents"]:
            debug(f"recalculate_hashes: repo content x1{x1}")
            if x1["url"] == x:
                jrepo["contents"][i]["hash"] = calc_sha1_hash(x)
                debug(f"recalculate_hashes: hash of {x} in {x1} written")
                break
            i = i + 1

    save_jrepo()


def remake_content(file, ask_subdir=True):
    if file is None:
        print("No exists packs... Create already!")
        return

    remDir = contents[file]["content"]["remote_parent"]
    directory = contents[file]["content"]["parent"]
    if ask_subdir:
        directory = input(f"Subdirectory to scan (in remote_parent={remDir}) -> ")
    if directory == "" and remDir == "":
        print("ERROR: No, make content from full root is a bad idea. Type 'assets' for use this folder. or use "
              "remote_parent")
        return

    content = contents[file]["content"]
    content["files"] = {}

    prefix = remDir + "/" + directory
    if len(directory) == 0 and len(remDir) == 0:
        prefix = "";

    elif len(directory) == 0 and len(remDir) != 0:
        prefix = remDir;

    elif len(directory) != 0 and len(remDir) == 0:
        prefix = directory;


    content["parent"] = directory
    for e in get_filepaths("./"):
        e = e[2::]
        if not e.startswith(prefix):
            continue;

        if _is_system_file(e):
            continue


        print(f"File {e} updated!")
        content["files"][e.replace(prefix + "/", "").replace(" ", "%20")] = {
            "hash": calc_sha1_hash(e)
        }

    open(file, "w").write(json.dumps(contents[file], indent='\t'))
    calc_sha1_hash(file)


def input_exists_content_file():
    if len(contents) == 0:
        return None

    i = 1
    c = [None]
    for x in contents:
        print(f" [{i}] {x}")
        c.append(x)
        i = i + 1

    inp = input("\t\t -> ")
    t = c[int(inp)]
    if t is None:
        print("Selected none...")
        return None
    debug(f"input_exists_content_file: selected = {t}")
    return t


def calc_sha1_hash(file):
    if Path(file).exists():
        with open(file, 'rb') as open_file:
            content = open_file.read()
            originContent = content

        if is_convert_line_end(file):
            # Windows ➡ Unix (before)
            content = content.replace(b'\r\n', b'\n')

            # Old macos ➡ Unix
            content = content.replace(b'\r', b'\n')

            if originContent != content:
                debug(f"CRLF -> LF: success for file {file}")

            with open(file, 'wb') as open_file:
                open_file.write(content)

        return hashlib.sha1(content).hexdigest()

    else:
        print(f"WARN: File not found {file}\nWARN: returned hash: \"\"(empty string)")
        return ""


def is_convert_line_end(file):
    for x in convert_line_ending_rules:
        if file.endswith(x):
            t = convert_line_ending_rules[x]
            debug(f"is_convert_line_end({file}): returned {t}")
            return t

    user = input("Convert CRLF -> LF for file type: " + file + "\n\t\t[Y/n] -> ")
    t = user == "Y" or user == "y"
    debug(f"is_convert_line_end({file}): returned {t}")
    return t


def get_filepaths(directory):
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    debug(f"get_filepaths({directory}) return {file_paths}")
    return file_paths  # Self-explanatory.


def _path_repair_1(rem, parent, file):
    if rem is None:
        rem = ""

    if parent is None:
        parent = ""

    if file is None:
        print("ERROR: File is None")
        return

    t = rem + "/" + parent + "/" + file
    if len(rem) == 0 and len(parent) == 0:
        return file

    elif len(rem) == 0 and len(parent) != 0:
        return parent + "/" + file

    elif len(rem) != 0 and len(parent) == 0:
        return rem + "/" + file

    return t


def _is_system_file(file_path):
    b = True
    for x in EXCLUDE_UNASSIGNED:
        if file_path.endswith(x):
            b = False
            break

    return not b


def debug(m):
    if DDEBUG:
        print(f"DEBUG: {m}")


if __name__ == '__main__':
    main()
