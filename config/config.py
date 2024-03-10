import os
from dotenv import load_dotenv

load_dotenv()
PASSWORD_SQL = os.getenv('PASSWORD_SQL')
HOST_SQL = os.getenv('HOST_SQL')
USER_SQL = os.getenv('USER_SQL')
DATABASE_SQL = os.getenv('DATABASE_SQL')
SQL_PORT = os.getenv('SQL_PORT')
TOKEN = os.getenv('TOKEN')
THIRD_PARTY_ID = os.getenv('THIRD_PARTY_ID')
THIRD_PARTY_ID_TWO = os.getenv('THIRD_PARTY_ID_TWO')
GROUP_LINK = os.getenv('GROUP_LINK')
