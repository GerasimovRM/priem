from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

LOGIN = config.get("MAIN", "LOGIN")
PASSWORD = config.get("MAIN", "PASSWORD")
SERVER_ADDRESS = config.get("MAIN", "MAIN_ADDRESS")
PARSER_URL = config.get("MAIN", "BASE_URL")
BASE_TIME_WAIT = config.get("MAIN", "BASE_TIME_WAIT")
