#!/usr/bin/python3
from pathlib import Path
import sys
import json
import os

try:
    filename = os.environ["map_input_file"]
    trimmed_filename = filename.replace("hdfs://ec2-18-208-114-108.compute-1.amazonaws.com:9000/input/", "").replace(".txt", "")
except KeyError as ex:
    print("Unable to find input file:\t" + ex)
    raise Exception
    
for line in sys.stdin:
    try:
        data = json.loads(line)

        for comment in data["response"]:
	        print("{}{}{}\t{}".format(trimmed_filename, "_", comment["id"], json.dumps(comment)))
    except Exception as ex:
        print("JSON error:\t {}".format(ex))