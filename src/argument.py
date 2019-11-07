import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", default="ast",
                    choices=["ast", "csi"],
                    help="select the mode of analysis")
parser.add_argument("-u", "--update", nargs="?", const=True,
                    help="update components/symbols or not")
# support Windows
if sys.platform == "win32":
    parser.add_argument("-d", "--dump", nargs=2,
                        default=[r"data\ex_dump_1.trc", r"data\ex_dump_2.trc"],
                        help="pass crash dump files")
    parser.add_argument("-s", "--source", nargs="?",
                        default=r"C:\hana",
                        help="source code path")
else:
    parser.add_argument("-d", "--dump", nargs=2,
                        default=["data/ex_dump_1.trc", "data/ex_dump_2.trc"],
                        help="pass crash dump files")
    parser.add_argument("-s", "--source", nargs="?",
                        default="/hana",
                        help="source code path")

__all__ = [
    "parser"
]
