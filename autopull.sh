cd /home/alex/Documents/DiscordTimeBox

git add .
git reset --hard HEAD
git pull

chmod +x ./autopull.sh
source ./env/bin/activate
nohup python3 -u ./main.py > output.log &
disown