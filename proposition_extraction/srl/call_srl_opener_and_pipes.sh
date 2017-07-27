#!/usr/bin/env bash

# Tests with srl from ixa pipes

docdir="$1"
outdir="$2"

lidport=1234 #opener lang id
tokport=1235 #opener tokenizer

pipesdir=/home/pablo/usr/local
srldir="$pipesdir/ixa-pipe-srl"
version=1
srljar="$srldir/IXA-EHU-srl/target/IXA-EHU-srl-$version.0.jar"

posjar="$pipesdir/ixa-pipe-pos/target/ixa-pipe-pos-1.4.4.jar"
posmodel="$pipesdir/ixa-pipe-pos/pos-models-1.4.0/en/en-maxent-100-c5-baseline-dict-penn.bin"


if [ ! -d "$outdir" ] ; then
  mkdir "$outdir"
  mkdir "$outdir/pos"
  mkdir "$outdir/tok"
  mkdir "$outdir/srl"
fi


for fn in $(ls "$docdir") ; do
  if [ -f "$outdir/srl/$fn.srl" ] ; then
      echo "- Skipping $outdir/srl/$fn.srl"
      continue

  echo -e "$fn\t$(date +"%T")"

  echo -e "  lid\t$(date +"%T")"
  lid=$(curl --data-urlencode "input=$(cat $docdir/$fn)&kaf=true" \
        http:$lidport -XPOST 2> /dev/null)

  echo -e "  toks\t$(date +"%T")"
  toks=$(curl --data-urlencode "input=$lid&kaf=true" \
        http://localhost:$tokport -XPOST 2> /dev/null)
  echo -e "$toks" > "$outdir/tok/$fn.tok.kaf"

  echo -e "  to_naf\t$(date +"%T")"
  cat "$outdir/tok/$fn.tok.kaf" | kaf-naf-parser --tonaf > \
      "$outdir/tok/$fn.tok.naf"

  echo -e "  pos\t$(date +"%T")"
  cat "$outdir/tok/$fn.tok.naf" | java -jar "$posjar" tag -m "$posmodel" > \
      "$outdir/pos/$fn.pos.naf" 2> /dev/null

  echo -e "  srl\t$(date +"%T")"
  cat "$outdir/pos/$fn.pos.naf" | java -Xms2500m -jar "$srljar" en \
      > "$outdir/srl/$fn.srl"
done

echo -e "\nDone. Creating tarballs\n"

tar -cvzf "$outdir/pos.tgz" "$outdir/pos"
[[ $(echo $?) -eq 0 ]] && rm -rf "$outdir/pos"
tar -cvzf "$outdir/tok.tgz" "$outdir/tok"
[[ $(echo $?) -eq 0 ]] && rm -rf "$outdir/tok"

