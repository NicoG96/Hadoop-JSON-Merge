# Hadoop JSON Merge

## Deliverables

* All deliverables are found in /out/
* Further documentation on project structure found in /docs/

## Overview

### Problem

* We have a web crawler that pulls .json data from articles on a periodic basis 
  * Files are composed of comments

* Files created by the crawler follow this pattern: {article_ID}_{timestamp}

  * Where the article ID is based on the current article the crawler is pulling from and the timestamp is when it pulled this data

* We have multiple files that match article ID but vary in their timestamps

* We want one file per article: it should contain every discrete comment from all files and contain no duplicates

### Solution

* MapReduce program using a distributed 4-node Hadoop cluster
  * A large dataset necesitates a more efficient algorithm to process these files in lieu of sequential processing
  
  * As such, this application uses Hadoop to process these files in parallel using MapReduce programming

* This program specifically utilizes Hadoop's streaming API, whereby processing is done via stdin and stdout and offloads the mapper and reducer functions to custom classes (Mapper.py and Reducer.py)

  * This was chosen in favor of the generic API as there were certain difficulties in classpath configuration and external jars that could not be resolved

  * Python was chosen as the language of choice for its competent standard library and inclusion of json parsing tools

* This application processes a set of files for one article ID and will append all unique identifying comment IDs into one structured json file

## Application

### Workflow

1. A sample set is defined and passed as an argument to the application

2. The application iteratively parses each file and prints out every comment ID and the corresponding metadata that accompanies it as a key/value pair for the Reducer to process

	* The comment ID, in conjuction with the article ID and timestamp, compose the entire key value of the Mapper's output: {article_ID}\_{timestamp}\_{comment_id}

3. Then, in Reducer.py, these key/value pairs are split by the default `\t` character

4. From there, the key is further broken down into its constituent parts, by splitting on every occurrence of `_`
	* This gives us the article ID, timestamp, and comment ID as individual variables in our program

5. Then, the comment IDs are appended to a class dictionary with its value set to a list containing the timestamp and the data it was passed with (the output value from the Mapper)

6. Every new line is then compared to the existing dictionary, to see whether a comment already exists
	* If it doesn't, it is simply appended to the dictionary
	* If it does exist, then a key lookup is done and the stored timestamp variable is compared to that of the current timestamp
		* Whichever has the most recent timestamp is placed into the dictionary

7. Finally, when the program has reached the end of the file list and there is no further processing to do, a function is called to print the class-level dictionary to stdout 

8. The dictionary is iterated over, and prints the unique comments into a structured JSON array, where it is then saved as a file in HDFS as a part-00000 file

### Example

Showing that Hadoop services are running, its version number, and java version:

![hadoop](https://i.imgur.com/iFSnx14.png)

Listing the files in HDFS to be processed:

![ls](https://i.imgur.com/lwlt7eU.png)

Running the Hadoop Streaming API with arguments configured likeso:

![cmd](https://i.imgur.com/OYGI31L.png)

An example of the output during the job:

![progress](https://i.imgur.com/G43tnL2.png)

Hadoop output from a successful run:

![success](https://i.imgur.com/7zyVZ6o.png)

An example of the HDFS output directory after invoking the program:

![ls2](https://i.imgur.com/4qlANL0.png)

Getting those files from HDFS using the following command:

![get](https://i.imgur.com/565FLoG.png)

Running shell commands on file to peek at its contents:

![cat](https://i.imgur.com/SRZJEoC.png)

Validating that the file is properly structured JSON:

![valid](https://i.imgur.com/TXyBH92.png)

### Issues / Limitations

#### Memory

The most glaring issue with this project was the memory limitations: EC2 instances were only running on 1GB of RAM, and from the cursory reading I've done, that's regarded as a near-inadequate amount for a Hadoop processor.  The overhead of running a Hadoop cluster eats up a lot of processing power by its own merit and compounding it with a large dataset presented even more problems:

This program generally only operates smoothly with a small dataset. Sets that approach more than 4 files almost universally fail every time.  The program is completely operational and produces the expected output when working with small datasets, but when given a large dataset to parse, it functionally breaks down to the point that the entire cluster is frozen and needs to be rebooted via the EC2 dashboard.

The fact that the larger the dataset, the higher the rate of failure lends credence to the suggestion that this is a memory issue. Moreover, runs that failed would occasionally complete successfully after a reboot of the EC2 instance -- further suggesting that the memory for these instances are reaching capacity. Put bluntly, this was a limitation I could not reconcile given the architecture I had to work with.

As a workaround, I resolved to manually separate these files into their own folders, grouped by article ID.  This way, the dataset is artificially restricted to its absolute minimum. Athough the initialization and extraction of the data is a bit more tedious, the output is fundamentally the same. After hours of troubleshooting and manually attempting to configure the memory limits in Hadoop configuration files, I found this was the only rational solution to my memory problems.

#### Hadoop Streaming API

If you look at my code you will notice that the Mapper and Reducer classes are written in Python. MapReduce programs in Hadoop are generally written in Java but I ran into some very inconvenient errors while using the Java SDK related to external jars (JSON parser) and their configuration in the Hadoop classpath.  Ultimately, it was something that I was unable to correct after hours of research so I resolved to outsource the work to a different, more functional programming language.

Scripting with a language outside of Java is made possible by Hadoop's streaming API, a jar file within the installation that runs MapReduce jobs via stdin and stdout.  This way, by writing to stdout, a mapper class from any language can utilize Hadoop's framework since it pipes the output from stdout as input for the Reducer class. Ultimately, the end result is functionally the same, it differs only in how it got there.  I found Python to be easier to work with as the standard library is more comprehensive and I'm much more familiar with Python.
