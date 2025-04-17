import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv(Path(__file__).parent / ".env")


class Config:
    DATABASE_DRIVER = os.environ.get("DATABASE_DRIVER")
    DATABASE_PATH = os.environ.get("DATABASE_PATH")

    def __init__(self):
        if not any([self.DATABASE_DRIVER, self.DATABASE_PATH]):
            print("ENV FILE NOT SET. EXITING. . .")
            sys.exit(1)
        self.DATABASE_URL = URL.create(
            drivername=self.DATABASE_DRIVER, database=self.DATABASE_PATH
        )


settings = Config()
