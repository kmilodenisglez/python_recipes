"""
Purpose

Shows how to use pynamodb with Amazon DynamoDB

source: https://github.com/pynamodb/PynamoDB
documentation: https://pynamodb.readthedocs.io/en/stable/tutorial.html#why-pynamodb
"""

import os
from datetime import datetime
from uuid import uuid4

# pynamodb lib imports
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, DynamicMapAttribute, BooleanAttribute, \
    NumberAttribute

aws_region = os.getenv('AWS_REGION_SERVER') or 'us-east-1'
db_settings_table_name = os.getenv('DB_TABLE_SETTINGS') or 'settings_table'


# A map attribute that supports declaring attributes (like an AttributeContainer)
# but will also store any other values that are set on it (like a raw MapAttribute).
#
# The SettingData class define a JSON data like this:
# {
#    'debug_mode_enabled': False,
#    'notification_enabled': False
# }
class SettingData(DynamicMapAttribute):
    debug_mode_enabled = BooleanAttribute(default_for_new=False)
    notification_enabled = NumberAttribute(default_for_new=2)


# model to describe Settings
#
# The Settings model define a JSON data like this:
# {
#   'slug': '5217ab3c-deaf-4064-9137-365fab0a907b',
#   'environment': 'dev',
#   'data': {
#       'debug_mode_enabled': False,
#       'notification_enabled': False
#    },
#   'created_at': '2023-06-25T19:19:24.598518+0000',
#   'updated_at': '2023-06-25T19:19:24.598518+0000'
# }
class Settings(Model):
    class Meta:
        table_name = db_settings_table_name
        # specifies the region
        region = aws_region

    slug = UnicodeAttribute(hash_key=True)
    environment = UnicodeAttribute(default_for_new="dev")
    created_at = UTCDateTimeAttribute(default_for_new=datetime.utcnow())
    updated_at = UTCDateTimeAttribute(default_for_new=datetime.utcnow())
    data = SettingData()


# get the first item in settings table
def get_first_item():
    results = Settings.scan(limit=1)
    try:
        item = next(results)
    except ScanError as ex:
        raise ex

    return item


# Scan filters example
def iterate_all_item():
    # Using only 5 RCU per second
    results = Settings.scan(rate_limit=5)
    while True:
        try:
            item = next(results)
        except StopIteration:
            break
        except ScanError as ex:
            raise ex
        else:
            # handle item
            print(item)


def update_using_params_example(model_instance: Model):
    # create a data object for -- update -- item
    data_setting_object = SettingData(
        debug_mode_enabled=False,
        notification_enabled=False
    )

    # -- update -- setting item [data.debug_mode_enabled, data.notification_enabled and updated_at]
    model_instance.update(
        actions=[
            Settings.updated_at.set(datetime.utcnow()),
            Settings.data.set(data_setting_object)
        ]
    )


def update_using_dict_example(model_instance: Model):
    data_setting_dict = {
        'debug_mode_enabled': True,
        'notification_enabled': False
    }
    settings_data_object = SettingData(**data_setting_dict)

    model_instance.update(
        actions=[
            Settings.updated_at.set(datetime.utcnow()),
            Settings.data.set(settings_data_object)
        ]
    )


if __name__ == '__main__':
    # create data object for -- insert -- item
    # omit the 'debug_mode_enabled' attribute because its default value is false
    data_setting1 = SettingData(
        notification_enabled=True
    )

    # generate slug partition-key attribute using uuid4
    slug = str(uuid4())
    # -- insert -- a setting item
    Settings(
        slug=slug,
        data=data_setting1
    ).save()

    # get previously saved Setting item using slug partition-key
    settings1 = Settings.get(slug)
    print("Show setting object: ", settings1)
    print("Show setting object like a JSON-serializable: ", settings1.to_simple_dict())

    update_using_dict_example(settings1)

    print("Show setting object: ", settings1)

    update_using_params_example(settings1)

    print("Show setting object: ", settings1)

    # -- delete -- item
    # settings1.delete()

    # for examples of creating and deleting tables see:
    # https://pynamodb.readthedocs.io/en/stable/tutorial.html#creating-the-table
    # https://pynamodb.readthedocs.io/en/stable/tutorial.html#deleting-a-table
