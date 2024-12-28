FIRST_BYTES = "$#$#$ SPLASHES FORMAT $#$#$"

class SplashesUnwrapper(object):
    """
    Convert "wrapped" splashes to plain text (used in minecraft resourcepack)
    Methods:
        wrapped_file_to_unwrapped(<wrapped-file-path>, <dest-for-minecraft-splashes-txt-file>)
        wrapped_splashes_to_unwrap_str(<wrapped-file-content>) => returns unwrapped splashes in string.
    """
    def __init__(self, is_debug):
        self.is_debug = is_debug


    def debug(self, msg):
        if self.is_debug:
            print(f"[SplashesUnwrapper:DEBUG] {msg}")


    def del_comment_line(self, line):
        if "//" not in line:
            return line

        cmt = line.rindex("//")
        self.debug(f"{cmt}: {line}")
        return line[:cmt]

    def wrapped_file_to_unwrapped(self, wrf, rf):
        """
        Unwrap splashes (file1 -> file2)
        :param rf: wrapped file path
        :param wrf: file for write unwrapped splashes
        """

        with open(wrf, 'r', encoding='utf-8') as input_file, open(rf, 'w', encoding='utf-8') as output_file:
            output_file.write(self.wrapped_splashes_to_unwrap_str(input_file.read()))

    def wrapped_splashes_to_unwrap_str(self, input_str: str):
        """
        Unwrap splashes (string)
        :param input_str: input str
        :return: output str
        """
        result_splashes = []
        required_bytes = False
        current_header = None

        for line in input_str.split("\n"):
            if line == FIRST_BYTES:
                required_bytes = True

            elif not required_bytes:
                raise IOError("Format header not found")

            elif len(line) == 0:
                pass  # pass if empty line

            elif line.startswith("//"):
                is_header = line.startswith("//---")
                if is_header:
                    current_header = line[5::]

                if current_header is not None:
                    self.debug(line)

            else:
                result_splashes.append(self.del_comment_line(line).strip())

        return "\n".join(sorted(result_splashes))


