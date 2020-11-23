from argument import parser
from function import best_matched
from persistence import load_functions

args = parser.parse_args()
functions = load_functions()


def function_match(func):
    if func in functions:
        component = functions[func]
    else:
        while True:
            if "::" in func:
                func = func[:func.rindex("::")]
                if func in functions:
                    component = functions[func]
                    break
            else:
                if func in functions:
                    component = functions[func]
                    break
                else:
                    component = ""
                    break
    return component


def to_component(func_info):
    name, source = func_info
    raw = name
    # get component by source
    if source:
        component = best_matched(source)
        # handle fake source
        if component == "UNKNOWN":
            component = function_match(name)
    # get component by name
    else:
        component = function_match(name)
    if component == "":
        component = raw
    return component
