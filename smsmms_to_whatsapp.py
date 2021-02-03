#! /usr/bin/env python3

import base64
import datetime
import json
import os
import sys
import xml.etree.ElementTree as ET

from typing import Dict


# map of phone number -> user names
USER_MAP: Dict[str, str] = {}


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
            phone_number = addr.attrib["address"].lstrip("+")
            if phone_number in USER_MAP:
                return USER_MAP[phone_number]
            else:
                full_name = input(f"Full name for phone number: {phone_number}: ").strip()
                USER_MAP[phone_number] = full_name
                return full_name

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


def main(groupname, fname):
    tree = ET.parse(fname)
    root = tree.getroot()

    try:
        os.mkdir(f"telegram-{groupname}")
    except FileExistsError:
        pass
    os.chdir(f"telegram-{groupname}")

    if os.path.exists("members.json"):
        with open("members.json") as f:
            USER_MAP.update(json.load(f))

    with open(f"WhatsApp Chat with {groupname}.txt", "w") as f:
        for msg in root:
            output = msg_to_text(msg)

            # todo - check encoding?
            f.write(output)
            f.write("\n")

    with open("members.json", "w") as f:
        json.dump(USER_MAP, f)


if __name__ == "__main__":
    groupname = sys.argv[1]
    fname = sys.argv[2]
    main(groupname, fname)