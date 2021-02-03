#! /usr/bin/env python3

import datetime
import json
import os
import sys
import urllib.request


OLD_NAME = [""]


def groupme_media_name(fname) -> str:
    """ image media from groupme urls is formatted oddly, like:
    828x809.jpeg.b083fc7771d848d78c8466f558202063

        Want to return:
    b083fc7771d848d78c8466f558202063.828x809.jpeg

    (video media is named fine, don't change)
    """
    res, ext, _id = fname.split(".")
    ext = "jpg" if ext == "jpeg" else ext
    return ".".join([_id, res, ext])


def download_file(url, fname):
    if os.path.exists(fname):
        return

    with urllib.request.urlopen(url) as _url:
        with open(fname, "wb") as f:
            f.write(_url.read())


def get_text(msg) -> str:
    text = msg["text"]

    for attachment in msg["attachments"]:
        if attachment["type"] in ["image", "video"]:
            # first download the file
            dst_file = attachment["url"].split("/")[-1]
            if attachment["type"] == "image":
                dst_file = groupme_media_name(dst_file)
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
        if " changed the group's name to " in msg["text"]:
            old_name = OLD_NAME[0]
            author, new_name = msg["text"].split(" changed the group's name to ")
            OLD_NAME.pop()
            OLD_NAME.append(new_name)
            # possible bug: might not escape group with double quote in name
            return f"{d_res} - {author} changed the subject from \"{old_name}\" to \"{new_name}\""

        if "event" in msg and msg["event"]["type"] == "group.avatar_change":
            url = msg["event"]["data"]["avatar_url"]
            # possible bug:
            # assume avatar is an image of type png or jpg (is this always correct?)
            ext = "png" if ".png." in url else "jpg"
            download_file(url, f"avatar.{ext}")

        return ""

    text = get_text(msg)
    return f"{d_res} - {msg['name']}: {text}"


def main(fname):
    chat_id = fname.split("/")[0]

    with open(fname) as f:
        j = json.load(f)

    dst = f"telegram-{chat_id}"
    try:
        os.mkdir(dst)
    except FileExistsError:
        pass
    os.chdir(dst)

    with open(f"WhatsApp Chat with {OLD_NAME[0]}.txt", "w") as f:
        for msg in j[::-1]:
            if o_msg := format_msg(msg):
                f.write(o_msg)
                f.write("\n")


if __name__ == "__main__":
    # gross arg parsing
    # first arg should be the original name of the group (groupme export doesnt say it???)
    OLD_NAME = [sys.argv[1]]
    # second arg should be the messages.json you got from groupme export
    fname = sys.argv[2]
    main(fname)
