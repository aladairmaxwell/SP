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
    ".DS_Store": False,
    ".blend": True,
    "desktop.ini": False,
    ".properties.disabled": True,
    ".gltf": True,
    ".bbmodel": True,
    ".gz": False,
    ".csv": True
}

IGNORE = [
    ".git",
    ".idea",
    ".nojekyll",
    ".DS_Store",
    "dynamicmcpack.repo.json",
    "dynamicmcpack.repo.build",
    ".gitignore",
    "files.csv",
    "files.csv.gz",
    "_info.txt",
    "README.md",
    ".py",
    "packsquash"
]


import hashlib
import os
import csv
from pathlib import Path
import shutil
import gzip


def debug(m):
    if False:
        print(f"DEBUG: {m}")





def get_filepaths(directory):
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename).replace("./", "")

            cont = False
            for x in IGNORE:
                if filepath.endswith(x) or filepath.startswith(x):
                    cont = True

            if cont:
                continue

            file_paths.append(filepath.replace("\\", "/"))  # Add it to the list.

    return file_paths  # Self-explanatory.


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


def fix_line_ending_and_return_hash(file):
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


def create_files_csv(directory, output_file=None):
    if output_file is None:
        output_file = f'{directory}/files.csv'

    files = get_filepaths(directory)

    print(output_file)
    with open(output_file, 'w', newline='\n') as csvfile:
        csv_writter = csv.writer(csvfile, delimiter=',',
                                 quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for file in files:
            file_rel = os.path.relpath(file, directory)
            file_hash = fix_line_ending_and_return_hash(file)
            file_size = os.path.getsize(file)

            row = [file_hash, file_size, file_rel]
            print(row)
            csv_writter.writerow(row)

    fix_line_ending_and_return_hash(output_file)
    print(f"Gzipped {output_file} -> {output_file}.gz")
    with open(output_file, 'rb') as f_in:
        with gzip.open(output_file + ".gz", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)




def update():
    saved_contents = []
    with open('contents.csv', newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in spamreader:
            saved_contents.append(row)


    for row in saved_contents:
        create_files_csv(row[1])
        row[2] = row[1] + "/files.csv.gz"
        row[3] = fix_line_ending_and_return_hash(row[2])

    print("Saving contents.csv")
    with open('contents.csv', 'w', newline='\n') as csvfile:
        csv_writter = csv.writer(csvfile, delimiter=',',
                                 quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in saved_contents:
            csv_writter.writerow(row)

    fix_line_ending_and_return_hash('contents.csv')


def main():
    update()



if __name__ == "__main__":
    main()