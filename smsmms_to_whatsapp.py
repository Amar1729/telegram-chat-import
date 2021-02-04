#! /usr/bin/env python3

import base64
import datetime
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

from pathlib import Path
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


def participants(msg) -> str:
    s = set(["+" + a.attrib['address'].lstrip("+") for a in msg.find("addrs").findall("addr")])
    return ", ".join(sorted(s))


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


def convert_3gpp(fname) -> str:
    """ MMS occasionally sends videos or gifs as .3gpp media files.
    Telegram will recognize these as video, but won't play them.
    If the user has ffmpeg installed, convert them to mp4.
    """
    try:
        output_mp4 = Path(fname).stem + ".mp4"
        result = subprocess.run(
            ["ffmpeg", "-i", fname, output_mp4],
            capture_output=True,
        )
        if result.returncode == 0:
            os.remove(fname)
            return output_mp4
    except FileNotFoundError:
        pass
    return fname


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
            basename = part.attrib["name"] if part.attrib["name"] != "null" else "media"
            # datestamp-originalname.newextension
            fname = f"{msg.attrib['date']}-{Path(basename).stem}.{CONTENT_MAP[ct]}"
            data = base64.b64decode(part.attrib["data"])

            with open(fname, "wb") as f:
                f.write(data)

            if ct == "video/3gpp":
                print("3gpp video found. Attempting conversion with ffmpeg.")
                fname = convert_3gpp(fname)

            return f"{fname} (file attached)"

    return ""


def msg_to_text(msg, allowed) -> str:
    if participants(msg) not in allowed:
        return ""

    datestamp = msg.attrib["date"]
    date = datetime.datetime.fromtimestamp(int(datestamp) / 1000)
    d_str = date.strftime("%-m/%d/%y %H:%M")

    author = determine_author(msg)
    text = download_msg(msg)
    return f"{d_str} - {author}: {text}"


def main(groupname, fname):
    tree = ET.parse(fname)
    root = tree.getroot()

    _convos = set()
    for msg in root:
        _convos.update([participants(msg)])

    convos = sorted(list(_convos))

    if len(convos) > 1:
        # this is somewhat hacky, because MMS addrs do not always have the country code
        # before the phone number. Parsing through all addrs and keeping track of the sender
        # and keeping track of all the country codes properly may be a bit more work
        # than is necessary yet.
        print("There are multiple conversations in this SMS/MMS backup.")
        print("(sometimes, this can happen if your own phone number does not show up in")
        print("all messages of a particular MMS group chat)")
        print(f"Please select which conversations you'd like to include in: '{groupname}'")
        print()
        for i, c in enumerate(convos):
            print(i, c)
        print()
        answer = input("Space-separated list of choices: ")

    allowed = [c for i, c in enumerate(convos) if i in map(int, answer.split(" "))]

    if os.path.exists("members.json"):
        with open("members.json") as f:
            USER_MAP.update(json.load(f))

    cur_dir = os.getcwd()

    try:
        os.mkdir(f"telegram-{groupname}")
    except FileExistsError:
        pass
    os.chdir(f"telegram-{groupname}")

    with open(f"WhatsApp Chat with {groupname}.txt", "w") as f:
        for msg in root:
            if output := msg_to_text(msg, allowed):

                # todo - check encoding?
                f.write(output)
                f.write("\n")

    os.chdir(cur_dir)

    with open("members.json", "w") as f:
        json.dump(USER_MAP, f)


if __name__ == "__main__":
    groupname = sys.argv[1]
    fname = sys.argv[2]
    main(groupname, fname)
