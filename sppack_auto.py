import json
import os.path

from dynamicpack_auto import get_filepaths

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



def run():
    print("SPPack automatization tool")
    print("")
    print("Select a hook")
    print("[1] pretty-print optimize")
    print("[2] lowercase all dirs")

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


if __name__ == "__main__":
    run()
