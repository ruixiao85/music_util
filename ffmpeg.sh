#!/usr/bin/env bash
# git bash

# /Music/music_util
docker build --rm --tag ffmpeg ffmpeg
cd ..

# /Music
docker run -it -v /`pwd`:/`pwd` -w /`pwd` ffmpeg bash
# which ffmpeg # /opt/conda/bin/ffmpeg
music_util/raw2mp3.py `which ffmpeg` "2Carol_圣歌" "testfolder"

