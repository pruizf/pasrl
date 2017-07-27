#!/usr/bin/env bash

# Tests with srl from ixa pipes

docdir="$1"
outdir="$2"
consts="$3"  # yes|no
coref="$4"

pipesdir=/home/pablo/usr/local

# tok
tokdir="$pipesdir/ixa-pipe-tok"
tokjar="$tokdir/target/ixa-pipe-tok-1.8.2.jar"

# pos
posdir="$pipesdir/ixa-pipe-pos"
posjar="$posdir/target/ixa-pipe-pos-1.4.4.jar"
posmodel="$posdir/pos-models-1.4.0/en/en-maxent-100-c5-baseline-dict-penn.bin"

# constituents
parserdir="$pipesdir/ixa-pipe-parse"
parserjar="$parserdir/target/ixa-pipe-parse-1.1.1.jar"
parsemodel="$parserdir/parse-models/en-parser-chunking.bin"

# srl
srldir="$pipesdir/ixa-pipe-srl"
version=1
srljar="$srldir/IXA-EHU-srl/target/IXA-EHU-srl-$version.0.jar"

# switch back to system ruby for coref module

#TODO: verify if this commendted out thing gets rid of the
# 'RVM is not a function' message
#[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"
rvm use system

if [ ! -d "$outdir" ] ; then
  mkdir "$outdir"
  mkdir "$outdir/pos"
  mkdir "$outdir/tok"
  mkdir "$outdir/srl"
fi

if [ "$consts" == 'yes' ]; then
    mkdir "$outdir/consts"
    mkdir "$outdir/coref"
    psf=".par"
fi

if [ "$consts" == 'yes' ]; then
    csf=".coref"
fi


for fn in $(ls "$docdir") ; do
#  if [ -f "$outdir/srl/$fn$psf$csf.srl.naf" ] && \
#     [ -s "$outdir/srl/$fn$psf$csf.srl.naf" ]; then
  if [ -f "$outdir/srl/$fn$psf$csf.srl.naf" ]; then
      echo "- Skipping $outdir/srl/$fn$csf$psf.srl.naf"
      continue
  fi
#  if [ $(wc -w "$docdir/$fn" | sed -e "s/ .*$//g") -gt 4000 ] ; then
#      echo "Too large $fn"
#      continue
#  fi
  echo -e "$fn\t$(date +"%T")"

  # tokenize
  echo -e "  toks\t$(date +"%T")"
  cat "$docdir/$fn" | java -jar  "$tokjar" tok -l en -n ptb > \
      "$outdir/tok/$fn.tok.naf" 2> /dev/null

  # POS tag
  echo -e "  pos\t$(date +"%T")"
  cat "$outdir/tok/$fn.tok.naf" | java -jar "$posjar" tag -m "$posmodel" > \
      "$outdir/pos/$fn.pos.naf" 2> /dev/null

  # constituent parsing
  if [ "$consts" == 'yes' ] ; then
      echo -e "  const\t$(date +"%T")"
      cat "$outdir/pos/$fn.pos.naf" | java -jar "$parserjar" \
          parse -m "$parsemodel" > "$outdir/consts/$fn.par.naf"
  fi

  # coreference
  if [ "$coref" == 'yes' ] ; then
      echo -e "  coref\t$(date +"%T")"
      # naf to kaf
      echo -e "     n2k\t$(date +"%T")"
      cat "$outdir/consts/$fn.par.naf" | kaf-naf-parser --tokaf > \
          "$outdir/consts/$fn.par.kaf"
      # coref
      echo -e "     coref\t$(date +"%T")"
      python -m corefgraph.process.file --reader KAF --file \
          "$outdir/consts/$fn.par.kaf" --language en > \
          "$outdir/coref/$fn.par.coref.kaf"
      # kaf to naf back
      echo -e "     k2n\t$(date +"%T")"
      cat "$outdir/coref/$fn.par.coref.kaf" | kaf-naf-parser --tonaf > \
          "$outdir/coref/$fn.par.coref.naf"
  fi

  echo -e "  srl\t$(date +"%T")"
  if [ "$consts" == 'yes' ] ; then
      if [ "$coref" == 'yes' ] ; then
          beforesrl="$outdir/coref/$fn.par.coref.naf"
          aftersrl="$outdir/srl/$fn.par.coref.srl.naf"
        else
          beforesrl="$outdir/consts/$fn.par.naf"
          aftersrl="$outdir/srl/$fn.par.srl.naf"
      fi
    else
      beforesrl="$outdir/pos/$fn.pos.naf"
      aftersrl="$outdir/srl/$fn.srl.naf"
  fi
  cat "$beforesrl" | java -Xms2500m -jar "$srljar" en > "$aftersrl"
      #> "$outdir/srl/$fn.srl"
      #> "$aftersrl"
done

#echo -e "\nDone. Creating tarballs\n"
#
#tar -cvzf "$outdir/pos.tgz" "$outdir/pos"
#[[ $(echo $?) -eq 0 ]] && rm -rf "$outdir/pos"
#tar -cvzf "$outdir/tok.tgz" "$outdir/tok"
#[[ $(echo $?) -eq 0 ]] && rm -rf "$outdir/tok"
#
