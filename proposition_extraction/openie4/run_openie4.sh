#!/usr/bin/env bash
# run open ie 4 jar on a directory, killing sleeping processes after

home=/home/pablo/projects/ie/iewk/openie4
indir=$1
outdir=$2
runner=$home/call_openie4.sh
piddir=$home/../pids
pidfile=$piddir/openie4-pids

[[ -f "$pidfile" ]] && rm "$pidfile"

[[ ! -d "$outdir" ]] && mkdir -p "$outdir"

[[ ! -d "$piddir" ]] && mkdir -p "$piddir"

# workaround spaces in paths
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

counter=0
for f in $(ls "$indir") ; do
  # only do if absent or empty
  if [[ ! -f "$outdir/$f" ]] || [[ ! -s "$outdir/$f" ]]; then
    echo "$f"
    $runner "$indir/${f}" "$outdir/${f}"
    sleep 10
    $home/stop_sleeping.sh
    counter=$((counter+1))
  else
    echo "- Skipping $f"
  fi
done

#secs=$(($counter * 4))
#echo "Waiting for ${secs} seconds"
#sleep $secs

$home/stop_sleeping.sh
