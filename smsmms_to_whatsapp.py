#! /usr/bin/env python3

import base64
import datetime
import os
import sys
import xml.etree.ElementTree as ET


CONTENT_MAP = {
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "video/3gpp": "3gpp",
    "video/mp4": "mp4",
}


def determine_author(msg) -> str:
    for addr in msg.find("addrs"):
        # mms codes:
        # 137: sender
        # 151: CC'd
        if addr.attrib["type"] == "137":
            return addr.attrib["address"]

    raise Exception("No sender found for msg")


def download_msg(msg) -> str:
    """ Returns plaintext if message is plaintext.
    if it is a media attachment, download the attached media and return its filename """

    for part in msg.find("parts"):
        ct = part.attrib["ct"]
        if ct == "application/smil":
            pass
        elif ct == "text/plain":
            return part.attrib["text"]
        elif ct in CONTENT_MAP:
            # todo - this doesnt always work?
            # may have to generate UUIDs or base off of timestamp for media
            basename = part.attrib["name"] if part.attrib["name"] != "null" else "media."
            fname = msg.attrib["date"] + "-" + ".".join(basename.split(".")[:-1]) + "." + CONTENT_MAP[ct]
            data = base64.b64decode(part.attrib["data"])

            with open(fname, "wb") as f:
                f.write(data)

            return f"{fname} (file attached)"

    return ""


def msg_to_text(msg) -> str:
    datestamp = msg.attrib["date"]
    date = datetime.datetime.fromtimestamp(int(datestamp) / 1000)
    d_str = date.strftime("%-m/%d/%y %H:%M")

    author = determine_author(msg)
    text = download_msg(msg)
    return f"{d_str} - {author}: {text}"


def main(fname):
    tree = ET.parse(fname)
    root = tree.getroot()

    try:
        os.mkdir("export")
    except FileExistsError:
        pass
    os.chdir("export")

    with open("output.txt", "w") as f:
        for msg in root:
            output = msg_to_text(msg)

            # todo - check encoding?
            f.write(output)
            f.write("\n")


if __name__ == "__main__":
    fname = sys.argv[1]
    main(fname)
