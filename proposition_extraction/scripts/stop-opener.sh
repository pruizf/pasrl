openerpids=../pids/opener-pids
for x in $(cat $openerpids) ; do
  kill $x
done
