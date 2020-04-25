# Hadoop JSON Merge

## Deliverables
* All deliverables are found in /out/
* Further documentation on project structure found in /docs/

## Problem

* We have a web crawler that pulls .json data from articles on a periodic basis 
  - Files are composed of comments

* Files created by the crawler follow this pattern: {article_ID}_{timestamp}

  - Where the article ID is based on the current article the crawler is pulling from and the timestamp is when it pulled this data

* We have multiple files that match article ID but vary in their timestamps

* We want one file per article: it should contain every discrete comment from all files and contain no duplicates

## Solution

* MapReduce program using a distributed 4-node Hadoop cluster
  - A large dataset necesitates a more efficient algorithm to process these files in lieu of sequential processing
  
  - As such, this application uses Hadoop to process these files in parallel using MapReduce programming

* This program specifically utilizes Hadoop's streaming API, whereby processing is done via stdin and stdout and offloads the mapper and reducer functions to custom classes (Mapper.py and Reducer.py)

  - This was chosen in favor of the generic API as there were certain difficulties in classpath configuration and external jars that could not be resolved

  - Python was chosen as the language of choice for its competent standard library and inclusion of json parsing tools

* This application processes a set of files for one article ID and will append all unique identifying comment IDs into one structured json file

## Process

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

## Example
Listing the files in HDFS to be processed:

![ls](https://i.imgur.com/lwlt7eU.png)

Running the Hadoop Streaming API with arguments configured likeso:

![cmd](https://i.imgur.com/OYGI31L.png)

An example of the output during the job:

![progress](https://i.imgur.com/G43tnL2.png)

A list of the HDFS output files:
