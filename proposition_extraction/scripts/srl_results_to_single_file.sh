#!/usr/bin/env bash

indir=$1
outfile=$1/../$(basename $1)_ALL.txt

if [ -f $outfile ] ; then
  rm $outfile
fi

echo -e "\nOUT $outfile\n"

for x in $(ls $indir/*_ana.naf) ; do
  #basename
  echo -e "\n== ${x/*\//} ==\n" >> $outfile
  cat $x >> $outfile
done
