#!/usr/bin/env python3

# jnm 20210915, 20230516
import os
import datetime
import logging
import pytz
import requests
from wyze_sdk import Client
from wyze_sdk.models.events import EventFileType

client = Client(
    email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD']
)
device_mac = os.environ['WYZE_DEVICE_MAC']

TIMEZONE = pytz.timezone('US/Eastern')


def get_latest_event_video_url():
    events = client.events.list(device_ids=[device_mac], limit=1)
    if not events:
        raise RuntimeError('Whoops, no events!')

    event = events[0]
    videos = [f for f in event.files if f.type == EventFileType.VIDEO]
    if len(videos) != 1:
        logging.warning(
            f'Expected 1 video but received {len(videos)} instead!'
        )

    return videos[0].url


HTML_OUTPUT_PATH = os.environ.get('HTML_OUTPUT_PATH', 'limbo-pics.html')
video_filename = os.path.join(os.path.dirname(HTML_OUTPUT_PATH), 'video.mp4')

# TODO: erase images from last run; only process event if it's new
video_url = get_latest_event_video_url()
with open(video_filename, 'wb') as video_file:
    video_file.write(requests.get(video_url).content)

# TODO: move to some kind of template file
html_output = f'''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Baltimore Node Limbo Camera</title>
  </head>
  <body>
    <div style="display: flex; flex-flow: column; width: 95%; height: 95%; position: absolute;">
      <div style="flex-shrink: 0;">
        <h1>This stuff will be thrown away!</h1>
        <p>⚠️ If you <a href="https://discuss.baltimorenode.org/t/limbo-cam/5945">cannot see the video</a>, try <strike>using Firefox</strike> downloading the video and playing it in VLC 🤦.</p>
        <p>
          Please post on <a href="https://discuss.baltimorenode.org/">https://discuss.baltimorenode.org/</a> <em>right now</em> if something here belongs to you. If you don't have an account there, send an email to members [at]
          discuss.baltimorenode.org instead. Do not assume that anything is safe until you receive acknowledgement from a member. Better yet: take your stuff home or put it on your member shelf!
        </p>
        <p>
          <small>
            Last updated: {datetime.datetime.now(tz=TIMEZONE)}<br>
            Video timestamps will be older if no motion was detected
          </small>
        </p>
      </div>
      <video controls style="flex-shrink: 1; min-width: 854px; min-height: 480px;" src="{video_filename}"></video>
    </div>
  </body>
</html>
'''
with open(HTML_OUTPUT_PATH, 'w') as f:
    f.write(html_output)
