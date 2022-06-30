from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

LOGIN = config.get("MAIN", "LOGIN")
PASSWORD = config.get("MAIN", "PASSWORD")
SERVER_ADDRESS = config.get("MAIN", "SERVER_ADDRESS")
PARSER_URL = config.get("MAIN", "PARSER_URL")
BASE_TIME_WAIT = int(config.get("MAIN", "BASE_TIME_WAIT"))
DEBUG = True if config.get("MAIN", "DEBUG") == "true" else False
SERVER_PARSER_WAIT = int(config.get("MAIN", "SERVER_PARSER_WAIT"))
