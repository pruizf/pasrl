#!/usr/bin/env bash
# run open ie 4 on a file in background, save pid so that can kill

home=/home/pablo/projects/ie/tools/openie/target/scala-2.10
myhome=/home/pablo/projects/ie/iewk/openie4
pidfile=$myhome/../pids/openie4-pids
parser_port=15000
srl_port=15001

#java -jar $home/openie.jar --parser-server http://localhost:$parser_port --srl-server http://localhost:$srl_port --split --ignore-errors --format column "$1" "$2" > /dev/null 2> /dev/null &> /dev/null &

java -jar $home/openie.jar --parser-server http://localhost:$parser_port --srl-server http://localhost:$srl_port --split --ignore-errors --format column "$1" "$2" &

echo $! >> $pidfile

