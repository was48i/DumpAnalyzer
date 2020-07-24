import sys
import argparse

parser = argparse.ArgumentParser()
# show AST workflow
parser.add_argument("-w", "--workflow", nargs=2,
                    help="Show our workflow.")
# comparing based on CSI
parser.add_argument("-d", "--dump", nargs=2,
                    help="Input crash dump files.")
# change source code path
if sys.platform == "win32":
    parser.add_argument("-s", "--source", nargs="?",
                        default=r"C:\hana-master",
                        help="Select source code path.")
else:
    parser.add_argument("-s", "--source", nargs="?",
                        default="/hana-master",
                        help="Select source code path.")
# update components/functions
parser.add_argument("-u", "--update", nargs="?", const=True,
                    help="Update components/functions.")
