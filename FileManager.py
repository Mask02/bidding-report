import os
import json


def write_data_into_json(filename, data):
    with open(filename + ".json", "w") as df:
        df.write(json.dumps(data))


def create_output_dir(bot_name):
    if not os.path.exists("output"):
        os.mkdir("output")

    if not os.path.exists("output/" + bot_name):
        os.mkdir("output/" + bot_name)
