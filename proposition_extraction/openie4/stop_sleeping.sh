# kill pids

home=/home/pablo/projects/ie/iewk
pidfile=$home/pids/openie4-pids

for p in $(cat $pidfile); do 
  kill -9 $p > /dev/null &> /dev/null
done
