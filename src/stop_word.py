import requests

from collections import Counter
from etl import ETL
from process import Process


class StopWord:
    """
    Count file names that can be filtered.
    """
    @staticmethod
    def count_word():
        cnt = 0
        file_names = []
        result = ETL().extract_word()
        for row in result:
            cnt += 1
            test_id, url = row
            print("{}, {}/{}".format(test_id, cnt, len(result)))
            try:
                if requests.get(url, verify=False).status_code == 200:
                    dump = requests.get(url, verify=False).content.decode("utf-8")
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
                file_name = path[path.rindex("/") + 1:] if "/" in path else path
                file_names.append(file_name)
        print(Counter(file_names))
