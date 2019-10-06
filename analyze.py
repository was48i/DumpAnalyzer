#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from clang.cindex import Config
from component import update_components, components
from persistence import dump_components, load_components


def csi_compare():
    pass


def ast_compare():
    pass


if __name__ == "__main__":
    src_path = r"/hana"
    symbols = dict()
    # load libclang.so
    lib_path = r"/usr/local/lib"
    if Config.loaded:
        pass
    else:
        Config.set_library_path(lib_path)
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dump", nargs=2, type=argparse.FileType("r"),
                        help="pass crash dump files")
    parser.add_argument("-m", "--mode", choices=["ast", "csi"],
                        help="select the mode of analysis")
    parser.add_argument("-u", "--update", nargs="?", const=True,
                        help="update components or not")
    args = parser.parse_args()
    # update components or not
    if args.update:
        update_components(src_path)
        dump_components(components)
    else:
        components = load_components()
