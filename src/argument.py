import argparse

parser = argparse.ArgumentParser()
# show AST workflow
parser.add_argument("-w", "--workflow", nargs=1,
                    help="Show our workflow.")
# comparing based on CSI
parser.add_argument("-d", "--dump", nargs=2,
                    help="Input crash dump files.")
# change source code path
parser.add_argument("-s", "--source", nargs="?",
                    default="/hana-master",
                    help="Select source code path.")
# do not filter stop words
parser.add_argument("-r", "--raw", nargs="?", const=True,
                    help="Do not filter stop words.")
# update components/functions
parser.add_argument("-u", "--update", nargs="?", const=True,
                    help="Update components/functions.")
