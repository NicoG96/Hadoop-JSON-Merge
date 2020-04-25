#!/usr/bin/python3
import sys
import os
import json


def update_dict(timestamp, comment_id, data):
    if comment_id not in comments:
        comments.update({comment_id: [timestamp, data]})
    else:
        if comments.get(comment_id)[0] < timestamp:
            comments.update({comment_id:[timestamp, data]})


def write_to_file():
    raw_data = [v[1] for _, v in comments.items()]
    sz = len(raw_data)
    i = 0

    print("[")
    while i < sz:
        print("{}{}".format(raw_data[i], "," if sz-1 != i else ""))
        i = i+1
    print("]")


comments = {}
separator = "\t"
current_article = None
article_id = None

for line in sys.stdin:
    metadata, data = line.strip().split(separator, 1)
    article_id, timestamp, comment_id = metadata.split("_", 2)
    update_dict(timestamp, comment_id, data)
write_to_file()