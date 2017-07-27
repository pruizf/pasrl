#!/usr/bin/env bash

# Calls ixa-pipe-srl but gives choice to use tokenization and pos-tagging
# from either opener web services or from ixa-pipes


mode=$1
indir="$2"
outdir="$3"
pidfile=srlpid

if [ $# -eq 0 ] ; then
    echo "Usage: $0 op|po indir outdir"
    exit
fi


if [ $mode = 'op' ] ; then
    # opener for tok and pos, pipes for srl
    ./call_srl_opener_and_pipes.sh "$2" "$3" &
    echo $! > $pidfile
elif [ $mode = 'po' ] ; then
    # pipes for everything
    ./call_srl_pipes_only.sh "$2" "$3" &
    echo $! > $pidfile
else
    echo "Mode is 'op' or 'po'"
    exit
fi
