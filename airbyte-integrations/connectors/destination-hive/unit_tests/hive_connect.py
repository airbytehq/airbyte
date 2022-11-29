from impala.dbapi import connect
import json
import logging
import sys

def run_query(cursor, query):
    print(query)
    try:
        res = cursor.execute(query)
        print(res)
        if (res is None):
            try:
                rows = cursor.fetchall()
                print(rows)
            except Exception as e:
                print(e)
        return
    except Exception as e:
        print(e)


if __name__ == "__main__":

    if (len(sys.argv) != 3):
        logging.error("Usage: python {} <secrets/config.json> <query-string>".format(sys.argv[0]))
        sys.exit(1)

    config_file = sys.argv[1]
    query = sys.argv[2]

    secrets = None

    try:
        f = open(config_file)
        secrets = json.load(f)
        f.close()
    except Exception as e:
        logging.error('Error reading secrets file', e)
        sys.exit(1)

    conn = connect(
        host = secrets["host"],
        port = secrets["port"],
        auth_mechanism = secrets["auth_type"],
        use_ssl = (True if secrets["use_ssl"] == "true" else False),
        use_http_transport = (True if secrets["use_http_transport"] == "true" else False),
        http_path = secrets["http_path"],
        user = secrets["user"],
        password = secrets["password"])

    cursor = conn.cursor()

    run_query(cursor, query)

    cursor.close()
    conn.close()
