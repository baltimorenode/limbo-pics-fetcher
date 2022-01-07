#!/usr/bin/env python3

# jnm 20210915
import cv2
import os
import datetime
import requests
import tempfile
from wyze_sdk import Client
from wyze_sdk.models.events import EventFileType

client = Client(
    email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD']
)
device_mac = os.environ['WYZE_DEVICE_MAC']


def get_latest_event_video_url():
    events = client.events.list(device_ids=[device_mac], limit=1)
    if not events:
        raise RuntimeError('Whoops, no events!')

    event = events[0]
    videos = [f for f in event.files if f.type == EventFileType.VIDEO]
    if len(videos) != 1:
        raise RuntimeError(
            f'Expected 1 video but received {len(videos)} instead!'
        )

    return videos[0].url


EVERY_N_FRAMES = os.environ.get('EVERY_N_FRAMES', 17)
IMAGE_OUTPUT_PATTERN = os.environ.get('IMAGE_OUTPUT_PATTERN', 'stills/{n}.jpg')
HTML_OUTPUT_PATH = os.environ.get('HTML_OUTPUT_PATH', 'limbo-pics.html')

# TODO: erase images from last run; only process event if it's new
video_url = get_latest_event_video_url()
image_files = []
with tempfile.NamedTemporaryFile() as video_tempfile:
    video_tempfile.write(requests.get(video_url).content)
    video_capture = cv2.VideoCapture(video_tempfile.name)
    try:
        frame_counter = 0
        while True:
            read_ok, frame = video_capture.read()
            if not read_ok:
                break
            if frame_counter % EVERY_N_FRAMES == 0:
                filename = IMAGE_OUTPUT_PATTERN.format(n=frame_counter)
                cv2.imwrite(filename, frame)
                image_files.append(filename)
            frame_counter += 1
    finally:
        video_capture.release()

# TODO: move to some kind of template file
html_output = (
    '<html><head><title>Baltimore Node Limbo Camera</title>'
    '<style>img {margin: 1em; border: 0.25em solid fuchsia; '
    'display: inline-block; width: 25%}</style></head>'
    '<body><h1>This stuff will be thrown away!</h1>'
    '<p>Please post on <a href="https://discuss.baltimorenode.org/">'
    'https://discuss.baltimorenode.org/</a> <em>right now</em> if something '
    "here belongs to you. If you don't have an account there, send an email "
    'to members [at] discuss.baltimorenode.org instead. Do not assume that '
    'anything is safe until you receive acknowledgement from a member. Better '
    'yet: take your stuff home or put it on your member shelf!</p>'
    f'<p><small>Last updated: {datetime.datetime.now()}</small></p>'
)
for image_file in image_files:
    html_output += f'<a href="{image_file}"><img src="{image_file}"></a>'
html_output += '</body></html>'
with open(HTML_OUTPUT_PATH, 'w') as f:
    f.write(html_output)
