import logger
import re
import utils
import workflow


class Detection(object):
    """
    Detect crash dump similarity through the mathematical model.
    """

    def __init__(self, paths):
        self.paths = paths

    @staticmethod
    def function_block(functions):
        blocks = []
        # function cleaning
        for func in functions:
            if "(" in func:
                func = func[:func.index("(")]
            if "<" in func:
                func = func[:func.index("<")]
            if re.match(r"^[a-z]+[ ]", func):
                func = func[func.index(" ")+1:]
            for block in func.split("::"):
                blocks.append(block)
        return blocks

    def detect_sim(self):
        result = []
        kdetector = workflow.Workflow()
        for path in self.paths:
            processed = kdetector.pre_process(path)
            message = kdetector.add_knowledge(processed)
            result.append(message)
        printer = logger.Logger()
        printer.dump_print(result)
        # small position first
        tool = utils.Utils()
        components_x = [i[0] for i in result[0][::-1]]
        components_y = [i[0] for i in result[1][::-1]]
        len_x = len(components_x)
        len_y = len(components_y)
        len_max = max(len_x, len_y)
        if len_x > len_y:
            indices = tool.lcs_index(components_x, components_y)
        else:
            indices = tool.lcs_index(components_y, components_x)
        # obtain feature list
        positions = []
        distances = []
        index_x, index_y = indices
        position_x = [len_x - i - 1 for i in index_x]
        position_y = [len_y - i - 1 for i in index_y]
        for i, j in zip(position_x, position_y):
            # calculate distance by blocks
            str_x = self.function_block(result[0][i][1])
            str_y = self.function_block(result[1][i][1])
            positions.append(max(position_x[i], position_y[j]))
            distances.append(tool.normalized_dist(str_x, str_y))
        features = list(zip(positions, distances))
        similarity = kdetector.calculate_sim(features, len_max)
        printer.formula_print(features, len_max, similarity)
