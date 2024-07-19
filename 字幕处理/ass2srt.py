import re
import sys


class Ass2srt:
    def __init__(self, filename):
        self.filename = filename
        self.load()

    def output_name(self, tag=None):
        outputfile = self.filename[0:-4]
        if tag:
            outputfile = outputfile+"."+tag
        return outputfile+".srt"

    def load(self, filename=None):
        if filename is None:
            filename = self.filename

        with open(file=filename, mode="r", encoding="utf-8") as f:
            data = f.readlines()

        self.nodes = []
        for line in data:
            if line.startswith("Dialogue"):
                line = line.lstrip("Dialogue:")
                node = line.split(",")
                node[1] = timefmt(node[1])
                node[2] = timefmt(node[2])
                node[9] = re.sub(r'{.*}', "", node[9]).strip()
                node[9] = re.sub(r'\\N', "\n", node[9])
                self.nodes.append(node)
                # print(f"{node[1]}-->{node[2]}:{node[9]}\n")

    def to_srt(self, name=None, line=0, tag=None):
        if name is None:
            name = self.output_name(tag=tag)
        with open(file=name, mode="w", encoding="utf-8") as f:
            index = 1
            for node in self.nodes:
                f.writelines(f"{index}\n")
                f.writelines(f"{node[1]} --> {node[2]}\n")
                if line == 1:
                    text = node[9].split("\n")[0]
                elif line == 2:
                    tmp = node[9].split("\n")
                    if len(tmp) > 1:
                        text = tmp[1]
                else:
                    text = node[9]
                f.writelines(f"{text}\n\n")
                index += 1
            # print(f"字幕转换完成:{self.filename}-->{name}")
            print(f"字幕转换成功")

    def __str__(self):
        return f"文件名:{self.filename}\n合计{len(self.nodes)}条字幕\n"


def timefmt(strt):
    strt = strt.replace(".", ",")
    return f"{strt}0"


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help=".ass file to convert")
    parser.add_argument("-s", "--suffix", default="zh", choices=["zh", "en", "fr", "de"],
                        help="add suffix to subtitles name")
    parser.add_argument("-l", "--line", type=int,
                        choices=[0, 1, 2], default=0, help="keep double subtitles")
    parser.add_argument("-i", "--info", action="store_true",
                        help="display subtitles infomation")
    parser.add_argument("-o", "--out", help="output file name")

    args = parser.parse_args()

    if args.file is None:
        parser.print_help()

    app = Ass2srt(args.file)
    if args.info:
        print(app)
        sys.exit()

    line = 0
    if args.line:
        line = args.line

    app.to_srt(name=args.out, line=line, tag=args.suffix)


if __name__ == "__main__":
    # main()
    ass_path = sys.argv[1]
    subtitles=Ass2srt(ass_path)
    subtitles.to_srt()
