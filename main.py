#! /usr/bin/env python3

import datetime
import json
import sys


def format_msg(msg) -> str:
    d = datetime.datetime.fromtimestamp(msg['created_at'])
    d_res = d.strftime("%-m/%d/%y, %H:%M")

    if msg["user_id"] == "system":
        return ""

    # add a check for text being empty? what does media look like?
    # should result in a line that looks like:
    # 6/21/20, 22:10 - Amar Paul: IMG-20200621-WA0000.jpg (file attached)
    return f"{d_res} - {msg['name']}: {msg['text']}"


def main(fname):
    chat_id = fname.split("/")[0]

    with open(fname) as f:
        j = json.load(f)

    with open(f"output-{chat_id}.txt", "w") as f:
        for msg in j:
            if o_msg := format_msg(msg):
                f.write(o_msg)
                f.write("\n")


if __name__ == "__main__":
    fname = sys.argv[1]
    main(fname)
