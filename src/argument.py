import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-u", "--update", nargs="?", const=True, help="Update components/functions.")
parser.add_argument("-t", "--train", nargs="?", const=True, help="Training for parameter tuning.")
parser.add_argument("-c", "--compare", nargs=2, help="Compare original call stacks.")
parser.add_argument("-d", "--detect", nargs=2, help="Detect crash dump similarity.")
