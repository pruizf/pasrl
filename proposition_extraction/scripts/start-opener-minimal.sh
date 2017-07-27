openerpids=../pids/opener-pids
language-identifier-server -p 1234 > /dev/null &> /dev/null &
echo $! > $openerpids
tokenizer-server -p 1235 > /dev/null &> /dev/null &
echo $! >> $openerpids
#pos-tagger-server -p 1236 > /dev/null &> /dev/null &
#echo $! >> $openerpids

