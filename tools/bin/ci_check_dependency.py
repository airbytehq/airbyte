import sys
import logging

LOGGING_FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
CONNECTOR_PATH = "airbyte-integrations/connectors/"



def main():
    change_file_path = ' '.join(sys.argv[1:])
    logging.info(f"Changed files path {change_file_path}")
    with open(change_file_path) as file:
        for line in file:
            if CONNECTOR_PATH in line:
                print(line)


if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
    main()
