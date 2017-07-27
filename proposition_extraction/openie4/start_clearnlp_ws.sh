#!/usr/bin/env bash
# start nlptools servers that openie 4.0 is gonna call

nlptools_home=/home/pablo/projects/ie/tools/nlptools
myhome=/home/pablo/projects/ie/iewk
parser_port=15000
srl_port=15001


if [[ -z $(netstat -tlnp | grep $parser_port) ]] \
  && [[ -z $(netstat -tlnp | grep $srl_port) ]]; then
  (cd $nlptools_home && sbt -J-Xmx2700M 'project nlptools-parse-clear' "run-main edu.knowitall.tool.parse.ClearDependencyParserMain --server --port $parser_port") &
  (cd $nlptools_home && sbt 'project nlptools-srl-clear' "run-main edu.knowitall.tool.srl.ClearSrlMain --server --port $srl_port") &
fi