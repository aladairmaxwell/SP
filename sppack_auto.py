import csv
import hashlib
import json
import os.path
import re
import struct

from PIL import Image
import matplotlib.pyplot as plt


from dynamicpack_auto import get_filepaths

DEBUG = True
IGNORE = [
    ".git",
    ".idea",
    "__pycache__"
]


def enablePrettyPrint():
    rebuildPrettyPrint(True)


def disablePrettyPrint():
    rebuildPrettyPrint(False)


def rebuildPrettyPrint(state: bool):
    for e in get_filepaths("."):
        isIgn = False
        for ign in IGNORE:
            ign = "./" + ign
            if (e.startswith(ign)):
                isIgn = True

        if (isIgn):
            continue

        if (e.endswith(".json")):
            cool_json = None
            with open(e, "r") as file:
                try:
                    cool_json = json.load(file)

                except Exception as err:
                    print(f"[ERROR] {err} while processing file {e}")

            if (cool_json != None):
                with open(e, "w") as file:
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
    dirs = open("content_directories.txt", "r").read().split("\n")
    with open("contents.csv", 'w', newline='\n') as csvfile:
        csv_writter = csv.writer(csvfile, delimiter=',',
                                 quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writter.writerow(["id", "work_dir", "files_list", "files_list_hash"])
        for dir in dirs:
            #with open(dir + "/files.csv", 'rb') as open_file:
            #    content = open_file.read()
            csv_writter.writerow([dir.replace("/", "_"), dir, dir + "/files.csv", "ff00ffffffffffffffffffffffff"])


def debug(m):
    if DEBUG:
        print(f"DEBUG: {m}")


def analyze():
    for path in get_filepaths("."):
        if re.search("[^a-z1-90_\\-./]", path) != None:
            print(path)


def fixPng(path, nx, ny):
    # Open the original image
    original_image = Image.open(path)

    # Create a new image with a solid color (white) background
    new_image = Image.new("RGBA", (nx, ny), (0, 0, 0, 0))

    # Paste the original image onto the center of the new image
    new_image.paste(original_image, (0, 0))

    # Save the result
    new_image.save(path)
    print(f"[Modify] Resized image in {path}")



def findBadPngResolution():
    for path in get_filepaths("."):
        if (path.endswith(".png")):
            #print(f"PNG FOUND {path}")
            try:
                with open(path, 'rb') as f:
                    data = f.read()

                size = get_image_info(data)

                if (size[0] % 16 == 0 and size[1] % 16 == 0):
                    continue

                print(f"Bad png {size} at {path}")
                fixPng(path, fix_png_dim(size[0]), fix_png_dim(size[1]))

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

def run():
    print("SPPack automatization tool")
    print("")
    print("Select a hook")
    print("[1] pretty-print optimize")
    print("[2] lowercase all dirs")
    print("[3] analyze")
    print("[4] update_contents_csv")
    print("[5] find all png with size % 16 != 0")

    cmd = input(" ---> ")
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


if __name__ == "__main__":
    run()
