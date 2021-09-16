### Sloppy quick example

Run via cron every 5 minutes:
```
nodepress@localhost:~/limbo-pics-fetcher$ crontab -l | tail -n 1
*/5 * * * * /home/nodepress/limbo-pics-fetcher/run.sh
```

Send output to a public directory:
```
nodepress@localhost:~/limbo-pics-fetcher$ cat run.sh
#!/bin/bash

cd /home/nodepress/limbo-pics-fetcher/

. e/bin/activate
script_dir="$(pwd)"
cd '/home/nodepress/www.baltimorenode.org/www/limbo-cam'
export IMAGE_OUTPUT_PATTERN='{n}.jpg'
export HTML_OUTPUT_PATH='index.html'
export WYZE_EMAIL='root+wyze@abcdefg.org'
export WYZE_PASSWORD='yum yum yummy'
export WYZE_DEVICE_MAC=0000000DECAF
python3 "$script_dir/get-limbo-pics.py"
```
