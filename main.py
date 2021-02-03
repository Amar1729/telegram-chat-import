#! /usr/bin/env python3

import datetime
import json
import sys
import urllib.request


OLD_NAME = [""]


def groupme_media_name(fname) -> str:
    """ media from groupme urls is formatted oddly, like:
    828x809.jpeg.b083fc7771d848d78c8466f558202063

        Want to return:
    b083fc7771d848d78c8466f558202063.828x809.jpeg
    """
    res, ext, _id = fname.split(".")
    ext = "jpg" if ext == "jpeg" else ext
    return ".".join([_id, res, ext])


def download_file(url, fname):
    with urllib.request.urlopen(url) as _url:
        with open(fname, "wb") as f:
            f.write(_url.read())


def get_text(msg) -> str:
    text = msg["text"]

    for attachment in msg["attachments"]:
        if attachment["type"] in ["image", "video"]:
            # first download the file
            dst_file = groupme_media_name(attachment["url"].split("/")[-1])
            download_file(attachment["url"], dst_file)

            # then update our text
            if text:
                text = f"{dst_file} (file attached)" + "\n" + text
            else:
                text = f"{dst_file} (file attached)"

    return text


def format_msg(msg) -> str:
    d = datetime.datetime.fromtimestamp(msg['created_at'])
    d_res = d.strftime("%-m/%d/%y, %H:%M")

    if msg["user_id"] == "system":
        return ""

    text = get_text(msg)
    return f"{d_res} - {msg['name']}: {text}"


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
