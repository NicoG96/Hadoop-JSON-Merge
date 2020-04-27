<br />

  <h1 align="center">Hadoop JSON Merge</h1>

  <p align="center">
    A tool to deduplicate JSON contents using Hadoop
  </p>

<!-- TABLE OF CONTENTS -->

## Table of Contents

* [About the Project](#about)
  * [Problem](#problem)
  * [Solution](#solution)
* [Application](#app)
  * [Development](#dev)
  * [Workflow](#workflow)
  * [Examples](#ex)
* [Issues](#issues)
  * [Memory](#mem)
  * [Hadoop Streaming API](#hadoop)



<!-- ABOUT THE PROJECT -->
## About the Project

* All deliverables are found in /out/
* Further documentation on project structure found in /docs/

<!-- PROBLEM -->
### Problem

* We have a web crawler that pulls .json data from articles on a periodic basis 
  * Files are composed of comments

* Files created by the crawler follow this pattern: {article_ID}_{timestamp}

  * Where the article ID is based on the current article the crawler is pulling from and the timestamp is when it pulled this data

* We have multiple files that match article ID but vary in their timestamps

* We want one file per article: it should contain every discrete comment from all files and contain no duplicates

<!-- SOLUTION -->
### Solution

* MapReduce program using a distributed 4-node Hadoop cluster
  * A large dataset necesitates a more efficient algorithm to process these files in lieu of sequential processing
  
  * As such, this application uses Hadoop to process these files in parallel using MapReduce programming

* This program specifically utilizes Hadoop's streaming API, whereby processing is done via stdin and stdout and offloads the mapper and reducer functions to custom classes (Mapper.py and Reducer.py)

  * This was chosen in favor of the generic API as there were certain difficulties in classpath configuration and external jars that could not be resolved

  * Python was chosen as the language of choice for its competent standard library and inclusion of json parsing tools

* This application processes a set of files for one article ID and will append all unique identifying comment IDs into one structured json file

<!-- APPLICATION -->
## Application

<!-- DEV -->
### Development

Configuring the Hadoop architecture proved no simple feat. Admittedly, it took me a couple of days to get it properly functioning. I referenced [this article](https://www.shubhamdipt.com/blog/how-to-setup-hadoop-in-aws-ec2-instances/), [this article](https://www.novixys.com/blog/setup-apache-hadoop-cluster-aws-ec2/), and finally [this article](https://medium.com/@jeevananandanne/setup-4-node-hadoop-cluster-on-aws-ec2-instances-1c1eeb4453bd) as my primary sources of information. Moreover, some additional documentation was required in order to understand how to utilize Hadoop's streaming API. I referenced [Apache's very own documentation](https://hadoop.apache.org/docs/r1.2.1/streaming.html) as well as a [tutorial](https://www.tutorialspoint.com/hadoop/hadoop_streaming.htm) from TutorialsPoint that I found helpful.

In the process of configuring the Hadoop cluster, I found that no one single article gave an answer. Rather, I had to reference all of them, see how they differed, and understand what one article had that the other didn't implement. This took a while to actually grasp, but it merely required a deeper understanding of Hadoop and what the configuration files are doing. To that end, I endeavored to *understand* what each step was doing from each tutorial. I got familiar with the technology and was able to successfully configure the cluster by applying what I had learned from each of the articles.

With the architecture in place, I then set out to program a solution that would fit the requirements outlined on Canvas.  I originally drafted my application in Java using the standard Hadoop API and got it successfully working.However, applying this application across a distributed machine engendered some errors I was ultimately incapable of resolving (see: [Issues](#issues)).

As a result, I implemented my solution using Hadoop's streaming API and found relative success.  It succeeded in that it was actually able to *run*, but the performance was not up to par, as outlined in [Issues](#issues). The execution flow of the program is outlined below, as well as an example run with pictures.

Ultimately, the solution works albeit for small datasets. I nonetheless endeavored to produce the deliverables for all article IDs, which can be found in /out/.  There are 50 structured, valid json files that contain all discrete comments from the corresponding article ID they originated from. The files solely contain the comment JSON object and all of the data that encompasses (the objects from the 'response' list in the original json files from /sample/).

<!-- WORKFLOW -->
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

<!-- EXAMPLE -->
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

<!-- ISSUES -->
## Issues / Limitations

<!-- MEMORY -->
### Memory

The most glaring issue with this project was the memory limitations: EC2 instances were only running on 1GB of RAM, and from the cursory reading I've done, that's regarded as a near-inadequate amount for a Hadoop processor.  The overhead of running a Hadoop cluster eats up a lot of processing power by its own merit and compounding it with a large dataset presented even more problems:

This program generally only operates smoothly with a small dataset. Sets that approach more than 4 files almost universally fail every time.  The program is completely operational and produces the expected output when working with small datasets, but when given a large dataset to parse, it functionally breaks down to the point that the entire cluster is frozen and needs to be rebooted via the EC2 dashboard.

The fact that the larger the dataset, the higher the rate of failure lends credence to the suggestion that this is a memory issue. Moreover, runs that failed would occasionally complete successfully after a reboot of the EC2 instance -- further suggesting that the memory for these instances are reaching capacity. Put bluntly, this was a limitation I could not reconcile given the architecture I had to work with.

As a workaround, I resolved to manually separate these files into their own folders, grouped by article ID.  This way, the dataset is artificially restricted to its absolute minimum. Athough the initialization and extraction of the data is a bit more tedious, the output is fundamentally the same. After hours of troubleshooting and manually attempting to configure the memory limits in Hadoop configuration files, I found this was the only rational solution to my memory problems.

<!-- HADOOP -->
### Hadoop Streaming API 

If you look at my code you will notice that the Mapper and Reducer classes are written in Python. MapReduce programs in Hadoop are generally written in Java but I ran into some very inconvenient errors while using the Java SDK related to external jars (JSON parser) and their configuration in the Hadoop classpath.  Ultimately, it was something that I was unable to correct after hours of research so I resolved to outsource the work to a different, more functional programming language.

Scripting with a language outside of Java is made possible by Hadoop's streaming API, a jar file within the installation that runs MapReduce jobs via stdin and stdout.  This way, by writing to stdout, a mapper class from any language can utilize Hadoop's framework since it pipes the output from stdout as input for the Reducer class. Ultimately, the end result is functionally the same, it differs only in how it got there.  I found Python to be easier to work with as the standard library is more comprehensive and I'm much more familiar with Python.