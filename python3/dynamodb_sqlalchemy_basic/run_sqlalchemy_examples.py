"""
Purpose

Shows how to use SQLAlchemy and PyDynamoDB with Amazon DynamoDB

https://github.com/passren/PyDynamoDB
"""

from pydynamodb import sqlalchemy_dynamodb
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.orm import sessionmaker

# sqlalchemy imports
from sqlalchemy_api import run_scenario, get_all_items, iterate_over_items, add_item_using_dict, \
    add_item_using_list, add_item_using_kwargs

# "dynamodb://{aws_access_key_id}:{aws_secret_access_key}@dynamodb.{region_name}.amazonaws.com:443"
conn_str = (
        "dynamodb://dynamodb.{region_name}.amazonaws.com:443"
        + "?verify=false"
)
conn_str = conn_str.format(
    region_name="us-east-1",
)
engine = create_engine(conn_str)


# SQLAlchemy schema Table: Represent a table in a database
settings_table: Table = Table("settings_table", MetaData(),
                              Column('slug', String, nullable=False),
                              Column('environment', String, nullable=False),
                              Column('data', String),
                              Column('created_at', String),
                              Column('updated_at', String),
                              )


if __name__ == '__main__':
    # Connection objects. In this way it also includes a sessionmaker.begin() method,
    # that provides a context manager which both begins and commits a transaction, as
    # well as closes out the Session when complete, rolling back the transaction if any errors occur.
    # https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.execute
    # https://docs.sqlalchemy.org/en/14/core/tutorial.html
    Session = sessionmaker(engine)

    # populate the "settings_table" table if it is empty
    run_scenario(Session, settings_table)

    # add item to settings_table using kwargs
    add_item_using_kwargs(Session, settings_table, slug='admin', environment='admin@localhost')
    # add item to settings_table using dict
    add_item_using_dict(Session, settings_table, {"slug": "sample_using_dict", "environment": "dev"})
    # add item to settings_table using list
    add_item_using_list(Session, settings_table, [{"slug": str(i), "environment": str(i)} for i in range(3)])
    # iterate over all elements
    iterate_over_items(Session, settings_table)
    # returns all elements as a list object
    items = get_all_items(Session, settings_table)
    print(items)
