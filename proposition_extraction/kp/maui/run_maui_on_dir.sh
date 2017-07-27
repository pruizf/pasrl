#!/usr/bin/env bash

indir="$1"
outdir="$2"
mauidir="/home/pablo/projects/ie/tools/RAKEt"
modeldir="$mauidir/data/models"
jar="$mauidir/maui.jar"
#model="$modeldir/keyword_extraction_model"
model="$modeldir/kw_fao780__model"
maxkps=50

if [ $# -eq 0 ] ; then
    echo "Usage: $0 indir outdir"
    exit
fi

[ ! -d "$outdir" ] && mkdir -p "$outdir"

for fn in $(ls "$indir"); do
    echo "$fn"
    java -Xmx1024m -jar "$jar" run "$indir/$fn" -m "$model" -v none -n $maxkps > "$outdir/$fn"
done
