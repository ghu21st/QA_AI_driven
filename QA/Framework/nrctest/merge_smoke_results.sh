pwd
if [ "$TESTSERVICE"==cloudtest ]
then
    smokeLog_dir=$TESTPATH/ev2/Scripts/Framework/nrctest/log
    echo $smokeLog_dir
else
    smokeLog_dir=/package/unarchive/Framework/nrctest/log
fi
for entry in "$smokeLog_dir"/*
do
 test=$(echo $entry| cut -d'-' -f 2)
 echo $test
 Result=`grep -Po '(?<=Assert recognition validation... )[^ ]+' /$entry/*.log`
 echo "$Result"
 if [ -z "$Result" ]; then
  echo "ERROR"
  tail -15 /$entry/*.log
 fi
 echo "------------------------"
done 