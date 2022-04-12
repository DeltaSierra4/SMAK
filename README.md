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
$ python3 socialmediaanalysis.py <name of your config file, default is config_sample.json>
```
6. The results of the analysis are printed out in format of JSON. `parse_results.json` stores results containing your posting behavior over time in different categories of posts, whereas `count_results.json` stores results pertaining to your posting behavior with respect to other Facebook users across time.
7. In addition, relevant wordclouds and charts will be generated in the results directory where the code is saved.

## Structure of the results directory

Each directory within the results directory will store Wordcloud results, keyterm collections, URL frequencies, and charts and graphs of relevant statistics based on categories and time.

* annual_cat, monthly_cat, global_cat: Results from each category of posts (comments, messages, or regular posts on news feed) grouped by year, month, or total timespan, respectively.
* annual_cross, monthly_cross, global_cross: Results from all category of posts grouped by year, month, or total timespan, respectively.

Within each subdirectory of post category (comments, messages, or posts) or directly in each "\_cross" subdirectory are directories that will store relevant results.

* sgrank, sgrank_hl: Wordcloud of key terms extracted by the SGRank algorithm on your posts or headlines from URLs linked, if any exist, respectively.
* textrank, textrank_hl: Wordcloud of key terms extracted by the TextRank algorithm on your posts or headlines from URLs linked, if any exist, respectively.
* wordcloud, wordcloud_hl: Wordcloud of most frequently occuring words in your posts or headlines from URLs linked, if any exist, respectively.
* wordcloud_users: Wordcloud of most frequently occuring words in your posts with respect to the user that you're interacting with.
* url_count: Bar charts of most frequently cited URLs.

## How to use the config.json file

The config.json file allows the user to set required variables for the script to run as well as customize results.

1. Basic fields
Unless otherwise stated, all entries and user names are expected to be enclosed in quotation marks.
* Language field: Set to "en" for English. May include "ko" and "jp" eventually.
* Username field: Write your Facebook username.
* Datadir field: Put the path to the directory containing your Social Media data. If it is installed in the same folder as the codebase, it is expected to be something like "<Folder name>", where <Folder name> is the folder that contains your Social Media data.
* Resultsdir field: Provide a name for the folder that will contain your results. Default is set to "results".
* Analysis_period field: Provide a combination of any of the following: `"monthly"`, `"annual"`, and `"global"`. The options must be enclosed in square brackets as shown in the example config.json file. Default is set to ["monthly"].
NB! It is strongly recommended to choose only one of the three options to keep runtime down to a minimum.
* Post_types field: List of types of posts you wish to analyze. Default is set to ["comments", "messages", "posts"]. All items must be kept in square brackets as shown in the sample configuration json file and must be any combination of the three available options above.
* Target_names: List of usernames that you wish to specifically analyze your interactions with. Default is set to an empty list, i.e. [].

2. Analyzer_config settings
Unless otherwise stated, all entries are expected to be in numeric format without quotation marks.
NB! It is recommended that you run the script with the default settings in the sample configuration json file.
* SGrank_ngram field: List of consecutive numbers indicating the number of words in a key-term group. Default is set to [1, 2, 3, 4, 5, 6]. The list must not be empty, must contain consecutive integers greater than 0, and all numbers must be written in ascending order. For example, the following would be considered illegal settings: [], [-1, 0, 1, 2], [3, 5, 4, 2]
* SGrank_norm and Textrank_norm fields: Sets the normalizer for keyterm extraction. The value can be one of the following: "lower", "lemma", and "" (a pair of quotation marks with nothing in between). Setting this field to "lower" writes all keyterms in lowercase, "lemma" reduces keyterms to their base forms (e.g. "is" is converted to "be", "going" is converted to "go", and "skies" is converted to "sky"), and "" leaves the words untouched.
* SGrank_top_count and Textrank_top_count fields: Number of top-scoring keywords to pull from each post based on their importance rank. Default is set to 0. If this field is set to 0, the script will use the values used in the SGrank_top_ratio and Textrank_top_ratio fields.
* SGrank_top_ratio and Textrank_top_ratio fields: Top percentile of top-scoring keywords to pull from each post (i.e. setting this value to 0.25 will pull only the top quartile of keywords based on their importance rank). Default is set to 0.3. The value must be in a floating-point number format between 0.0 and 1.0 inclusive. If this field is set to 0.0, the script will use the values used in the SGrank_top_count and Textrank_top_count fields.
NB! For the SGrank_top_count-SGrank_top_ratio pair and the Textrank_top_count-Textrank_top_ratio pair, both values cannot be set to 0. Either one must be set to a legal value for the script to run.

3. SMAKstats_config settings
All entries must be integers without quotation marks.
* Keyterm_limit field: Number of most frequently occurring unique keyterms and expressions to include in the wordcloud for keyterm frequency. Default is set to 100. Value must be set to a positive integer.
* Wordcount_limit field: Number of most frequently occurring unique words to include in the wordcloud for word frequency. Default is set to 500. Value must be set to a positive integer.

4. Visualizer_config settings
All entries must be positive integers without quotation marks.
* Wordcloud_width field: Width of the keyterm frequency wordcloud output. Default is set to 1600.
* Wordcloud_height field: Width of the keyterm frequency wordcloud output. Default is set to 1200.
NB! The Wordcloud for word frequency will have double the size to incorporate more words.
* Wordcloud_limit field: Minimum number of unique keywords required to generate a wordcloud. Default is set to 200.
* URL_chart_upper_limit field: Number of top most frequently cited URLs to be listed in the result chart. Default is set to 30.
* URL_chart_lower_limit field: Minimum number of cited URLs required to generate a result chart. Default is set to 5.
* Min_data_count field: Minimum number of unique users required to generate a result chart for periodical post statistics. Default is set to 5.
* Max_data_count field: Maximum number of unique users to be displayed in the periodical post statistics. Default is set to 20. When the user has interacted with more than this number in a given period, then the script will divide this value by half and obtain statistics from the top half users and bottom half users. For example, if the value is set to 40 and the user has interacted with 55 users in the month of March 2021, then the script will display result charts showing statistics from the top 20 users and bottom 20 users.
NB! URL_chart_upper_limit must be greater than URL_chart_lower_limit, and Max_data_count must be greater than Min_data_count.