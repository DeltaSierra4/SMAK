from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import matplotlib.pyplot as plt
#import numpy as np
#import pandas as pd
import os


"""
	Result visualizer utility module for the Social Media Analytics Kit.
	Transforms the JSON objects containing word frequency data and keyword
	tables into word clouds depending on the frequency of tokens and creates
	charts based on frequency of URL citations.

	@author: DeltaSierra4
"""


def wordcloud_gen(result_dic):
	for set_type, batch in result_dic.items():
		if set_type.split("_")[1] == "cat":
			wordcloud_gen_cat(result_dic[set_type], set_type)
		else:
			wordcloud_gen_cross(result_dic[set_type], set_type)
	return


def wordcloud_gen_cat(result_dic, set_type):
	create_dir(set_type)
	for cat, cat_results in result_dic.items():
		cat_dir = os.path.join(set_type, cat)
		create_dir(cat_dir)
		for stat, stat_results in cat_results.items():
			if "count" in stat or "statistics" in stat:
				continue
			stat_dir = os.path.join(cat_dir, stat)
			create_dir(cat_dir)
			for time, counts in stat_results.items():
				time_dir = os.path.join(stat_dir, time)
				create_dir(time_dir)
				file_name = os.path.join(time_dir, stat + ".png")
				counts_dic = {pair[0]: pair[1] for pair in counts}
				wordcloud = WordCloud(
					background_color="white", width=1000, height=1000,
					normalize_plurals=True, stopwords=STOPWORDS
				).generate_from_frequencies(counts_dic)
				wordcloud.to_file(file_name)
	return


def wordcloud_gen_cross(result_dic, set_type):
	return


def url_chart_gen(result_dic):
	return


def create_dir(path):
	if not os.path.exists(path):
		os.mkdir(path)
