#/bin/bash
WAVE_DIR=$1

for f in $WAVE_DIR/*.wav; do
  t=$(echo $f | sed 's/\.wav$/.txt/');
  o=$(echo $f | sed 's/\.wav$/.textgrid/');
  #echo "processing..."$f" and "$t" output to "$o
  python2.7 alignbysentence.py $f $t $o
done