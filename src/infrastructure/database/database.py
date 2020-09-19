import logging
import os
import re

from sqlalchemy import (Column, ForeignKey, MetaData, String, Table, Text,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
logger = logging.getLogger(__name__)


class Database:
    db_engine = None

    def __init__(self, connection_url):
        self.db_engine = create_engine(connection_url, echo=True)
        if connection_url.startswith('sqlite'):
            db_file = re.sub("sqlite.*:///", "", connection_url)
            os.makedirs(os.path.dirname(db_file), exist_ok=True)
            logger.info(f'sqlite database created at "{db_file}"')

    def create_tables(self):
        metadata = MetaData()

        Table(
            'artist',
            metadata,
            Column('id', String, primary_key=True),
            Column('name', String),
            Column('url', String),
        )

        Table(
            'music',
            metadata,
            Column('id', String, primary_key=True),
            Column('name', String),
            Column('url', String),
            Column('language', String),
            Column('text', Text),
            Column('artist_id', None, ForeignKey('artist.id')),
        )

        try:
            metadata.create_all(self.db_engine)
            logger.info("Tables created")
        except Exception as e:
            logger.error("Error occurred during Table creation!")
            logger.error(e)

    def execute_query(self, query='', variables=()):
        if query == '':
            return

        with self.db_engine.connect() as connection:
            try:
                connection.execute(query, variables)
                logger.info(query)
            except Exception as e:
                logger.error(e)
