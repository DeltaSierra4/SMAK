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
* matplotlib 3.4.1
* wordcloud 1.8.1

## How to use (Facebook & Messenger)

1. Clone/download the SMAK repository to a directory of your choice.
2. Install dependencies with the following command:
```
$ pip install -r requirements.txt
```
3. Obtain your post data from Facebook. This can be done by Pressing the user menu on the top right hand corner, go to Settings & Privacy > Settings > Your Facebook Information > Download Your Information.
* Deselect all except Posts, Comments, and Messages, select the date range you wish to examine, then use the following settings: Format: JSON, Media Quality: Low
* Press Create File when you're ready to download your posts. This can take a while.
4. Download and unzip all .zip files created in the same directory as the SMAK codebase.
5. Run the following command in the current directory.
```
$ python3 socialmediaanalysis.py <name of directory containing all Facebook & Messenger data> <your name on Facebook and Messenger>
```
6. The results of the analysis are printed out in format of JSON. `parse_results.json` stores results containing your posting behavior over time in different categories of posts, whereas `count_results.json` stores results pertaining to your posting behavior with respect to other Facebook users across time.
7. In addition, relevant wordclouds and charts will be generated in the results directory where the code is saved.

## Structure of the results directory

Each directory within the results directory will store Wordcloud results, keyterm collections, URL frequencies, and charts and graphs of relevant statistics based on categories and time.

* annual_cat, monthly_cat, global_cat: Results from each category of posts (comments, messages, or regular posts on news feed) grouped by year, month, or total timespan, respectively.
* annual_cross, monthly_cross, global_cross: Results from all category of posts grouped by year, month, or total timespan, respectively.

Within each subdirectory of post category (comments, messages, or posts) or directly in each _cross subdirectory are directories that will store relevant results.

* sgrank, sgrank_hl: Wordcloud of key terms extracted by the SGRank algorithm on your posts or headlines from URLs linked, if any exist, respectively.
* textrank, textrank_hl: Wordcloud of key terms extracted by the TextRank algorithm on your posts or headlines from URLs linked, if any exist, respectively.
* wordcloud, wordcloud_hl: Wordcloud of most frequently occuring words in your posts or headlines from URLs linked, if any exist, respectively.
* wordcloud_users: Wordcloud of most frequently occuring words in your posts with respect to the user that you're interacting with.
* url_count: Bar charts of most frequently cited URLs.
