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
                        default=[r"data\bt_dump_1.trc", r"data\bt_dump_2.trc"],
                        help="pass crash dump files")
    parser.add_argument("-s", "--source", nargs="?",
                        default=r"C:\hana",
                        help="source code path")
else:
    parser.add_argument("-d", "--dump", nargs=2,
                        default=["data/bt_dump_1.trc", "data/bt_dump_2.trc"],
                        help="pass crash dump files")
    parser.add_argument("-s", "--source", nargs="?",
                        default="/hana",
                        help="source code path")
# data validation
parser.add_argument("--stats", nargs="?", const=True,
                    help="data validation mode")


__all__ = [
    "parser"
]
