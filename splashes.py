SOURCE_FILE = "splashes-with-metadata.txt"
OUTPUT_FILE = "sp_splashes/assets/minecraft/texts/splashes.txt"
DEBUG = False


def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")


def del_comment_line(line):
    if "//" not in line:
        return line

    cmt = line.rindex("//")
    debug(f"{cmt}: {line}")
    return line[:cmt]


def main():
    result_splashes = []
    s = open(SOURCE_FILE, 'r').read()
    required_bytes = False
    current_header = None

    for line in s.split("\n"):
        if line == "$#$#$ SPLASHES FORMAT $#$#$":
            required_bytes = True

        elif not required_bytes:
            raise IOError("format header not found")

        elif len(line) == 0:
            pass  # pass if empty line

        elif line.startswith("//"):
            is_header = line.startswith("//---")
            if is_header:
                current_header = line[5::]

            if current_header is not None:
                print(line)


        else:
            result_splashes.append(del_comment_line(line).strip())

    open(OUTPUT_FILE, "w").write("\n".join(sorted(result_splashes)))


if __name__ == "__main__":
    main()
