
#!/bin/bash

# Your YouTube streaming key
YT_KEY="wv5f-kxt7-aars-mr7e-byht"

while true; do
  ffmpeg -re -stream_loop -1 \
    -i rickroll.mp4 \
    -c:v libx264 -preset ultrafast -tune zerolatency \
    -maxrate 2000k -bufsize 4000k \
    -g 30 -r 24 \
    -c:a aac -b:a 128k -ar 44100 \
    -f flv rtmp://a.rtmp.youtube.com/live2/$YT_KEY

  sleep 2
done
