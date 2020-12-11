import requests

from collections import Counter
from etl import ETL
from process import Process


class StopWord(object):
    """
    Count file names that can be filtered.
    """
    @staticmethod
    def file_name(path):
        if "/" not in path:
            return path
        else:
            path = path[path.rindex("/") + 1:]
            return path

    def count_word(self):
        cnt = 0
        source = []
        result = ETL().extract_word()
        for row in result:
            cnt += 1
            test_id, url = row
            print("{}, {}/{}".format(test_id, cnt, len(result)))
            try:
                if requests.get(url, verify=False).status_code == 200:
                    dump = requests.get(url, verify=False).content.decode("latin-1")
                    processed = Process(dump).pre_process()
                else:
                    dump = ETL().extract_cdb(test_id)
                    processed = Process(dump).internal_process()
            except IndexError:
                continue
            except UnicodeDecodeError:
                continue
            for frame in processed:
                _, path = frame
                source.append(self.file_name(path))
        print(Counter(source))
