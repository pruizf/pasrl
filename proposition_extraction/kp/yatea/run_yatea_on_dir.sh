#!/usr/bin/env bash

# Runs Yatea client by Johan Ferguth on a directory

TAG=$1  # give "tag" as $1 if wanna run treetagger
TGR=/home/pablo/usr/local/tree-tagger-lin/cmd/tree-tagger-english
YATBASEDIR=/home/pablo/projects/ie/tools/Yatea
YATEXEDIR=/home/pablo/projects/ie/tools/Yatea/Yatea

# in and outdir in same directory as yatea
#INDIR=$YATBASEDIR/enb_docs_to_add_kp_extraction_to
#TAGGEDDIR=$YATBASEDIR/enb_docs_to_add_kp_extraction_to_ttg
TAGGEDDIR=$YATBASEDIR/transcripts_utf8_text_ttg
#TODO: indir and taggeddir as arguments


if [ "$1" = "tag" ] ; then
    if [ ! -d $TAGGEDDIR ] ; then
      mkdir -p $TAGGEDDIR
    fi

    echo "Running treetagger"
    for fn in $(ls $INDIR) ; do
      echo "  t $fn"
      if [ -z $(echo $fn | grep html) ]; then
          cat $INDIR/$fn | $TGR > $TAGGEDDIR/${fn/txt/ttg.txt}
        else
          cat $INDIR/$fn | $TGR > $TAGGEDDIR/${fn/.html/_html.ttg.txt}
      fi
    done
fi

echo "Running yatea"
for fn in $(ls $TAGGEDDIR) ; do
  echo "  y $fn"
  (cd $YATEXEDIR && perl ./ExtractTermeYatea.pl $TAGGEDDIR/$fn)
done