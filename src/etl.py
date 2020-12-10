import configparser
import os
import re
import requests
import hashlib

from connection import MongoConnection, SqlConnection
from datetime import datetime
from knowledge import Knowledge
from process import Process


class ETL(object):
    config = configparser.ConfigParser()
    path = os.path.join(os.getcwd(), "settings.ini")
    config.read(path)
    # SQL
    qdb_uri = config.get("sql", "qdb_uri")
    cdb_uri = config.get("sql", "cdb_uri")
    # MongoDB
    host = config.get("mongodb", "host")
    port = config.getint("mongodb", "port")
    db = config.get("mongodb", "db")
    coll = config.get("mongodb", "coll_data")

    def extract_qdb(self):
        set_schema = """SET SCHEMA TESTER;"""
        extract_content = """
        SELECT TEST_MANY.ID, TEST_MANY.START_TIME, TEST_MANY.LINK, TEST_MANY.BUG_ID
        FROM
            (
                SELECT TEST_CASES.ID, TEST_CASES.START_TIME, TEST_LOG_FILES.LINK, TEST_COMMENTS.BUG_ID
                FROM TEST_CASES
                    JOIN TEST_LOG_FILES ON TEST_CASES.ID = TEST_LOG_FILES.ID_TEST_CASE
                    JOIN
                    (
                        SELECT ID_TEST_CASE, MAX(ID_COMMENT) AS ID
                        FROM TEST_REVIEW
                        WHERE TEST_CASE_CLASSIFICATION = 'known'
                        GROUP BY ID_TEST_CASE
                    ) AS TEST_VALID
                    ON TEST_CASES.ID = TEST_VALID.ID_TEST_CASE
                    JOIN TEST_COMMENTS ON TEST_VALID.ID = TEST_COMMENTS.ID
                    JOIN TEST_PROFILES ON TEST_CASES.ID_TEST_PROFILE = TEST_PROFILES.ID
                    JOIN MAKES ON TEST_PROFILES.ID_MAKE = MAKES.ID
                WHERE TEST_CASES.START_TIME BETWEEN '2020-08-01' AND '2020-08-31'
                    AND TEST_LOG_FILES.DUMP_TYPE = 'CRASH'
                    AND TEST_LOG_FILES.LINK NOT LIKE '%recursive.trc%'
                    AND TEST_COMMENTS.BUG_ID != 0
                    AND MAKES.BUILD_PURPOSE = 'G'
                    AND (MAKES.COMPONENT = 'HANA' OR MAKES.COMPONENT = 'Engine')
            ) AS TEST_MANY
            JOIN
            (
                SELECT TEST_CASES.ID, COUNT(TEST_LOG_FILES.LINK) AS NUM
                FROM TEST_CASES
                    JOIN TEST_LOG_FILES ON TEST_CASES.ID = TEST_LOG_FILES.ID_TEST_CASE
                    JOIN
                    (
                        SELECT ID_TEST_CASE, MAX(ID_COMMENT) AS ID
                        FROM TEST_REVIEW
                        WHERE TEST_CASE_CLASSIFICATION = 'known'
                        GROUP BY ID_TEST_CASE
                    ) AS TEST_VALID
                    ON TEST_CASES.ID = TEST_VALID.ID_TEST_CASE
                    JOIN TEST_COMMENTS ON TEST_VALID.ID = TEST_COMMENTS.ID
                    JOIN TEST_PROFILES ON TEST_CASES.ID_TEST_PROFILE = TEST_PROFILES.ID
                    JOIN MAKES ON TEST_PROFILES.ID_MAKE = MAKES.ID
                WHERE TEST_CASES.START_TIME BETWEEN '2020-08-01' AND '2020-08-31'
                    AND TEST_LOG_FILES.DUMP_TYPE = 'CRASH'
                    AND TEST_LOG_FILES.LINK NOT LIKE '%recursive.trc%'
                    AND TEST_COMMENTS.BUG_ID != 0
                    AND MAKES.BUILD_PURPOSE = 'G'
                    AND (MAKES.COMPONENT = 'HANA' OR MAKES.COMPONENT = 'Engine')
                GROUP BY TEST_CASES.ID
            ) AS TEST_ONLY
            ON TEST_MANY.ID = TEST_ONLY.ID
        WHERE TEST_ONLY.NUM = 1
        ORDER BY TEST_MANY.START_TIME DESC;
        """
        with SqlConnection(self.qdb_uri).connection as sql:
            sql.execute(set_schema)
            result = sql.execute(extract_content).fetchall()
        return result

    def extract_cdb(self, test_id):
        extract_content = """
        SELECT HANAQA.CRASHES.CALLSTACK_STRING
        FROM HANAQA.QADB_CRASHES
            JOIN HANAQA.CRASHES
            ON HANAQA.QADB_CRASHES.CRASH_ID = HANAQA.CRASHES.CRASH_ID
        WHERE HANAQA.QADB_CRASHES.TEST_CASE_ID = {}
        UNION ALL
        SELECT BUGZILLA.CRASHES.CALLSTACK_STRING
        FROM HANAQA.QADB_CRASHES
            JOIN BUGZILLA.CRASHES
            ON HANAQA.QADB_CRASHES.CRASH_ID = BUGZILLA.CRASHES.CRASH_ID
        WHERE HANAQA.QADB_CRASHES.TEST_CASE_ID = {};
        """.format(test_id, test_id)
        with SqlConnection(self.cdb_uri).connection as sql:
            result = sql.execute(extract_content).fetchall()
        return result[0][0]

    def extract_source(self):
        set_schema = """SET SCHEMA TESTER;"""
        extract_content = """
        SELECT TEST_MANY.ID, TEST_MANY.LINK
        FROM
            (
                SELECT TEST_CASES.ID, TEST_CASES.START_TIME, TEST_LOG_FILES.LINK
                FROM TEST_CASES
                    JOIN TEST_LOG_FILES ON TEST_CASES.ID = TEST_LOG_FILES.ID_TEST_CASE
                    JOIN TEST_PROFILES ON TEST_CASES.ID_TEST_PROFILE = TEST_PROFILES.ID
                    JOIN MAKES ON TEST_PROFILES.ID_MAKE = MAKES.ID
                WHERE TEST_CASES.START_TIME >= ADD_MONTHS(TO_DATE(CURRENT_DATE), -1)
                    AND TEST_LOG_FILES.DUMP_TYPE = 'CRASH'
                    AND TEST_LOG_FILES.LINK NOT LIKE '%recursive.trc%'
                    AND MAKES.BUILD_PURPOSE = 'G'
                    AND (MAKES.COMPONENT = 'HANA' OR MAKES.COMPONENT = 'Engine')
            ) AS TEST_MANY
            JOIN
            (
                SELECT TEST_CASES.ID, COUNT(TEST_LOG_FILES.LINK) AS NUM
                FROM TEST_CASES
                    JOIN TEST_LOG_FILES ON TEST_CASES.ID = TEST_LOG_FILES.ID_TEST_CASE
                    JOIN TEST_PROFILES ON TEST_CASES.ID_TEST_PROFILE = TEST_PROFILES.ID
                    JOIN MAKES ON TEST_PROFILES.ID_MAKE = MAKES.ID
                WHERE TEST_CASES.START_TIME >= ADD_MONTHS(TO_DATE(CURRENT_DATE), -1)
                    AND TEST_LOG_FILES.DUMP_TYPE = 'CRASH'
                    AND TEST_LOG_FILES.LINK NOT LIKE '%recursive.trc%'
                    AND MAKES.BUILD_PURPOSE = 'G'
                    AND (MAKES.COMPONENT = 'HANA' OR MAKES.COMPONENT = 'Engine')
                GROUP BY TEST_CASES.ID
            ) AS TEST_ONLY
            ON TEST_MANY.ID = TEST_ONLY.ID
        WHERE TEST_ONLY.NUM = 1
        ORDER BY TEST_MANY.START_TIME DESC;
        """
        with SqlConnection(self.qdb_uri).connection as sql:
            sql.execute(set_schema)
            result = sql.execute(extract_content).fetchall()
        return result

    @staticmethod
    def serialize(sequence):
        cpnt_order = [seq[0] for seq in sequence]
        func_block = []
        for functions in [seq[1] for seq in sequence]:
            blocks = []
            for func in functions:
                if "(" in func:
                    func = func[:func.index("(")]
                if "<" in func:
                    func = func[:func.index("<")]
                if re.match(r"^[a-z]+[ ]", func):
                    func = func[func.index(" ") + 1:]
                for block in func.split("::"):
                    blocks.append(block)
            func_block.append(blocks)
        return cpnt_order, func_block

    @staticmethod
    def check_sum(func_block):
        text = ""
        for blocks in func_block:
            for block in blocks:
                text += block
        return hashlib.md5(text).hexdigest()

    def format_dump(self):
        cnt = 0
        documents = []
        result = self.extract_qdb()
        for row in result:
            cnt += 1
            test_id, time_stamp, url, bug_id = row
            print("{}, {}/{}".format(test_id, cnt, len(result)))
            try:
                if requests.get(url, verify=False).status_code == 200:
                    dump = requests.get(url, verify=False).content.decode("latin-1")
                    processed = Process(dump).pre_process()
                else:
                    dump = self.extract_cdb(test_id)
                    processed = Process(dump).internal_process()
            except IndexError:
                continue
            sequence = Knowledge().add_knowledge(processed)
            cpnt_order, func_block = self.serialize(sequence)
            data = dict()
            data["test_id"] = test_id
            data["time_stamp"] = int(datetime.timestamp(time_stamp))
            data["cpnt_order"] = cpnt_order
            data["func_block"] = func_block
            data["bug_id"] = bug_id
            data["md5sum"] = self.check_sum(func_block)
            documents.append(data)
        with MongoConnection(self.host, self.port) as mongo:
            collection = mongo.connection[self.db][self.coll]
            collection.drop()
            collection.insert_many(documents)