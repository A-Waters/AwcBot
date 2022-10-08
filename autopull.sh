#!/bin/bash
cd /home/alex/Documents/DiscordTimeBox

pkill python3 -u alex

git add .
git reset --hard HEAD
git pull

source ./env/bin/activate
nohup python3 -u ./main.py > output.log &
deactivate
disown