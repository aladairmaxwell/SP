from dynamicpack_auto import get_filepaths
import json

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





def run():
    print("SPPack automatization tool")
    print("")
    print("Select a hook")
    print("[1] pretty-print optimize")

    cmd = input(" ---> ")
    if (cmd == "1"):
        i = input("[E]nable or [D]isable pretty print?\n ->> ")
        if i.lower() == "e":
            enablePrettyPrint()


        elif (i.lower() == "d"):
            disablePrettyPrint()

        else:
            print("failed to recognize command")


if __name__ == "__main__":
    run()
