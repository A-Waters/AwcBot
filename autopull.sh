cd /home/alex/Documents/DiscordTimeBox

git add .
git reset --hard HEAD
git pull

nohup python3 -u ./main.py > output.log &