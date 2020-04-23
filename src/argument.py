import argparse

parser = argparse.ArgumentParser()
# mode selection
parser.add_argument("-m", "--mode", default="ast",
                    choices=["ast", "csi"],
                    help="select the mode of analysis")
# do not filter stop words
parser.add_argument("-r", "--raw", nargs="?", const=True,
                    help="do not filter stop words")
# show AST workflow
parser.add_argument("-w", "--workflow", nargs=1,
                    help="show our workflow")
# comparing based on CSI
parser.add_argument("-d", "--dump", nargs=2,
                    help="input crash dump files")
# change source code path
parser.add_argument("-s", "--source", nargs="?",
                    default="/hana-master",
                    help="source code path")
# update components/functions
parser.add_argument("-u", "--update", nargs="?", const=True,
                    help="update components/functions")
