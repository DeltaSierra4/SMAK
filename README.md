# SMAK: Social Media Analytics Kit
Social Media Analytics Kit to analyze posting patterns of users on Facebook & Messenger.

## features

* Collect insight into your posting behavior and pattern on Facebook & Messenger with Python-based NLP package Textacy.
* Performs basic statistics calculation including (but not limited to) word count and word frequency to complex operations such as keyterm extraction.
* View various post statistics organized with respect to time, target user, and type of post.
* Produces word clouds based on set of keywords.
* Future implementation: Sentiment detection, multiple language support, expansion to other social media platforms.

## Installation

**Dependencies**: The following dependencies are required to run SMAK on your machine:

* Python 3.6+
* Textacy 0.10.1
* SpaCy 2.3.5
* plac 0.9.6

## How to use (Facebook & Messenger)

1. After installing the above dependencies, download the SMAK codebase to a directory of your choice.
2. Obtain your post data from Facebook. This can be done by Pressing the user menu on the top right hand corner, go to Settings & Privacy > Settings > Your Facebook Information > Download Your Information.
* Deselect all except Posts, Comments, and Messages, select the date range you wish to examine, then use the following settings: Format: JSON, Media Quality: Low
* Press Create File when you're ready to download your posts. This can take a while.
3. Download and unzip all .zip files created in the same directory as the SMAK codebase.
4. Run the following command in the current directory.
```
$ python3 socialmediaanalysis.py <name of directory containing all Facebook & Messenger data>
```
