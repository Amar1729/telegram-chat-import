# Telegram Chat Importers

As of January 2021, Telegram now offers a built-in feature to [import chat history from other apps](https://telegram.org/blog/move-history). However, that functionality is currently limited to WhatsApp, Line, and KakaoTalk.

Telegram's import (from WhatsApp) feature works by importing a text file that WhatsApp exports from a chat. Luckily this text file has a simple format, so we can reformat exported data from other chat apps into the WhatsApp format and just import that into Telegram.

### Chat Export Format

When exporting chats from WhatsApp, you get text files that are roughly formatted like so:

```
7/18/20, 21:07 - First Last: Hello world
7/18/20, 21:07 - First Last: media.jpg (file attached)
7/18/20, 21:08 - First Last: This is a long
multiline
message
```

These scripts take exported data from other chat apps and reformat them to look like this. I have not tested replies (which WhatsApp supports, but SMS/GroupMe do not), and likes are not saved since Telegram does not support them. Telegram does not import changes to the group chat name or avatar.

## General Usage

The scripts in this directory require a group name (can be arbitrary) as the first argument, and a specific file containing the exported data as the second argument (this differs based on which chat you are exporting from).

```
# for sms/mms
python3 smsmms_to_whatsapp.py "roommate chat" sms-20210203161451.xml

# for groupme
python3 groupme_to_whatsapp.py "roommate chat" 11339841/message.json
```

## Supported Chats

- SMS/MMS
- GroupMe

### SMS/MMS

Exporting SMS/MMS data can be done on Android with the "SMS Backup and Restore", which can export SMS and MMS (including group MMS) chats to XML. Currently it does NOT support RCS chats.

Once you have the XML file, the [`smsmms_to_whatsapp.py`](./smsmms_to_whatsapp.py) can be run to convert the XML to a directory containing any media (images or video) included in the chat as well as a `.txt` file.

### 3gpp Conversion

Some SMS clients will share gifs or small video as `3gpp`-formatted video (commonly used format over MMS), which Telegram will recognize as a video but won't play natively. If you have `ffmpeg` installed, the sms script will automatically convert any 3gpp video to mp4.

### GroupMe

Exporting GroupMe chat data can only be done from the web version (`https://web.groupme.com/chats`) by going to settings and selecting specific chats to export. You do NOT need to include media with the export - the exported data contains URLs to all media that you've shared that will be downloaded by the Python script.

Once you have the exported data, you can run the `groupme_to_whatsapp.py` on the `message.json` included in the ZIP file. This may work slowly based on how much media you have shared in the GroupMe chat, since it has to download all the media.

## Importing to Telegram

With large exports, I have found the easiest way is the zip up the resulting directory, transfer it to my phone, and decompress it there. After that, use a file explorer to select all the files (all media and the text file), and then "share with" Telegram. Telegram will automatically recognize this share as containing exported chat data in the form of a text file, and you can create a new chat from resulting dialog window.

Telegram will import your data and hopefully match contact names with your actual contacts (I have found this to be somewhat hit-or-miss, and probably depends on some server-side code that is not configurable currently).
