hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.7.3.jar \
-D mapred.job.name="python" \
-files Mapper.py,Reducer.py \
-mapper Mapper.py \
-reducer Reducer.py  \
-input /input \
-output /output \
-verbose