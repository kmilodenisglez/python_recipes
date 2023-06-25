import json
import os
from decimal import Decimal

from aws_lambda_powertools import Logger
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.testing.schema import Table

logger = Logger()


def get_sample_setting_data(setting_file_name):
    """
    Gets sample setting data, either from a local file or by first downloading it from
    the Amazon DynamoDB developer guide.

    :param setting_file_name: The local file name where the setting data is stored in JSON format.
    :return: The setting data as a dict.
    """
    try:
        with open(setting_file_name) as setting_file:
            setting_data = json.load(setting_file, parse_float=Decimal)
    except FileNotFoundError:
        print(f"File {setting_file_name} not found.")
        raise
    else:
        return setting_data[:]


def populate_table(session_instance: object, table: Table, setting_data: list):
    if isinstance(session_instance, Session):
        logger.info("populate %s table with %s ... collection", table.name, setting_data[:1])
        session_instance.execute(table.insert(), setting_data)
        logger.info("%s table has been populated successfully.", table.name)


def get_all_items(session: sessionmaker, table: Table):
    stmt1 = select(table)  # .where(table.c.slug != "spongebob")

    with session.begin() as s:
        items = s.execute(stmt1).fetchall()
        return items


def iterate_over_items(session: sessionmaker, table: Table):
    stmt1 = select(table)  # .where(table.c.slug != "spongebob")

    with session.begin() as s:
        for row in s.execute(stmt1):
            print(row)


def add_item_using_kwargs(session: sessionmaker, table: Table, **kwargs):
    try:
        with session.begin() as s:
            s.execute(table.insert().values(kwargs))
    except OperationalError as err:
        logger.error(err)


def add_item_using_dict(session: sessionmaker, table: Table, item: dict):
    try:
        with session.begin() as s:
            s.execute(table.insert().values(item))
    except OperationalError as err:
        logger.error(err)


def add_item_using_list(session: sessionmaker, table: Table, item: list):
    try:
        with session.begin() as s:
            s.execute(table.insert(), item)
    except OperationalError as err:
        logger.error(err)


def run_scenario(session: sessionmaker, table: Table):
    print('-' * 88)
    print("Welcome to the getting started demo of Amazon DynamoDB using SQLAlchemy.")
    print('-' * 88)

    stmt1 = select(table)
    with session.begin() as s:
        items = s.execute(stmt1).first()
        # if settings table is empty
        if items is None:
            current_dir = os.path.dirname(__file__)
            collection_file = os.path.abspath(os.path.join(current_dir, './settingsdata.json'))
            setting_data: list = get_sample_setting_data(collection_file)
            # we populate the tbl_settings table using setting_data
            populate_table(s, table, setting_data)
        else:
            logger.info("%s table is already populated", table.name)
