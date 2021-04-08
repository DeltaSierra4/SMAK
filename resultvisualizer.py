from wordcloud import WordCloud, STOPWORDS
from collections import defaultdict
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
	results_dir = "results"
	create_dir(results_dir)
	for set_type, batch in result_dic.items():
		set_dir = create_dir(results_dir, set_type)
		if set_type.split("_")[1] == "cat":
			for cat, cat_results in batch.items():
				cat_dir = create_dir(set_dir, cat)
				wordcloud_gen_cross(batch[cat], set_type, cat_dir)
		else:
			wordcloud_gen_cross(result_dic[set_type], set_type, set_dir)


def wordcloud_gen_cross(result_dic, set_type, init_path):
	for stat, stat_results in result_dic.items():
		width = 1600
		height = 1200
		if "count" in stat or "statistics" in stat:
			continue
		elif "wordcloud" in stat:
			width *= 2
			height *= 2
		stat_dir = create_dir(init_path, stat)
		if "users" not in stat:
			for time, counts in stat_results.items():
				time_dir = create_dir(stat_dir, time)
				file_name = os.path.join(time_dir, stat + ".png")
				counts_dic = {pair[0]: pair[1] for pair in counts}
				wordcloud = WordCloud(
					background_color="white", width=width, height=height,
					normalize_plurals=True, stopwords=STOPWORDS
				).generate_from_frequencies(counts_dic)
				wordcloud.to_file(file_name)
		else:
			for user, user_results in stat_results.items():
				user_dir = create_dir(stat_dir, user)
				for time, counts in user_results.items():
					counts_dic = {pair[0]: pair[1] for pair in counts}
					if len(counts_dic.keys()) < 200:
						# To prevent spamming tiny wordclouds, we set the
						# limit to wordclouds with more than 200 words.
						# TODO: Set up a configuration system to set this?
						continue
					time_dir = create_dir(user_dir, time)
					file_name = os.path.join(time_dir, stat + ".png")
					wordcloud = WordCloud(
						background_color="white", width=width, height=height,
						normalize_plurals=True, stopwords=STOPWORDS
					).generate_from_frequencies(counts_dic)
					wordcloud.to_file(file_name)
				if len(os.listdir(user_dir)) == 0:
					os.rmdir(user_dir)


def url_chart_gen(result_dic):
	results_dir = "results"
	create_dir(results_dir)
	for set_type, batch in result_dic.items():
		set_dir = create_dir(results_dir, set_type)
		if set_type.split("_")[1] == "cat":
			for cat, cat_results in batch.items():
				cat_dir = create_dir(set_dir, cat)
				urlchart_gen_cross(batch[cat], set_type, cat_dir)
		else:
			urlchart_gen_cross(result_dic[set_type], set_type, set_dir)


def urlchart_gen_cross(result_dic, set_type, init_path):
	for stat, stat_results in result_dic.items():
		if "count" not in stat:
			continue
		stat_dir = create_dir(init_path, stat)
		for time, counts in stat_results.items():
			time_dir = create_dir(stat_dir, time)
			file_name = os.path.join(time_dir, stat + ".png")

			# Only show top 30 results for now.
			counts_top = counts[:30]
			counts_dic = {pair[0]: pair[1] for pair in counts_top}
			plt.xticks(rotation=90)
			plt.gcf().subplots_adjust(bottom=0.5)
			plt.bar(counts_dic.keys(), counts_dic.values())
			plt.savefig(file_name)
			plt.clf()


def stat_chart_gen(result_dic):
	results_dir = "results"
	create_dir(results_dir)
	for set_type, batch in result_dic.items():
		if "global" in set_type:
			# A temporal chart for global statistics makes no sense.
			continue
		set_dir = create_dir(results_dir, set_type)
		if set_type.split("_")[1] == "cat":
			for cat, cat_results in batch.items():
				cat_dir = create_dir(set_dir, cat)
				statchart_gen_cross(batch[cat], set_type, cat_dir)
		else:
			statchart_gen_cross(result_dic[set_type], set_type, set_dir)


def statchart_gen_cross(result_dic, set_type, init_path):
	for stat, stat_results in result_dic.items():
		if "statistics" not in stat:
			continue
		stat_dir = create_dir(init_path, stat)
		stat_combiner = defaultdict(lambda: {})
		for time, stats in stat_results.items():
			for stat_type, value in stats.items():
				if "_only" in stat_type:
					stat_avg = "_".join([stat_type.split("_")[0], "avg"])
					stat_med = "_".join([stat_type.split("_")[0], "med"])
					stat_max = "_".join([stat_type.split("_")[0], "max"])
					stat_min = "_".join([stat_type.split("_")[0], "min"])
					stat_std = "_".join([stat_type.split("_")[0], "std"])
					stat_combiner[stat_avg][time] = value[1]
					stat_combiner[stat_med][time] = value[1]
					stat_combiner[stat_max][time] = value[1]
					stat_combiner[stat_min][time] = value[1]
					stat_combiner[stat_std][time] = value[1]
				else:
					if isinstance(value, (int, float)):
						stat_combiner[stat_type][time] = value
					else:
						stat_combiner[stat_type][time] = value[1]
		for stat_type, stat_dic in stat_combiner.items():
			file_name = os.path.join(stat_dir, stat_type + ".png")
			time_per = stat_dic.keys()
			stat_vals = stat_dic.values()
			plt.xticks(rotation=90)
			plt.gcf().subplots_adjust(bottom=0.25)
			plt.plot(time_per, stat_vals)
			plt.title(stat)
			plt.xlabel(stat_type)
			plt.ylabel('value')
			plt.savefig(file_name)
			plt.clf()


def stat_chart_gen_count(pruned_count_dic):
	return


def create_dir(path, addn_path=None):
	if addn_path is not None:
		path = os.path.join(path, addn_path)
	if not os.path.exists(path):
		os.mkdir(path)
	return path
