import configparser

config = configparser.ConfigParser()
main_section = config["MAIN"]

LOGIN = main_section["LOGIN"]
PASSWORD = main_section["PASSWORD"]
ZIP_DIR = main_section["ZIP_DIR"]
DATA_DIR = main_section["DATA_DIR"]
