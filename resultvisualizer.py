from wordcloud import WordCloud, STOPWORDS
from collections import defaultdict
import matplotlib.pyplot as plt
# from PIL import Image
# import numpy as np
# import pandas as pd
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


# TODO: Find a way to display the longest posts and/or the most random
# posts?
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


def stat_chart_gen_count(count_dic):
	extra_step_per_cat = {
		"comments": 2,
		"messages": 1,
		"posts": 0,
	}
	results_dir = "results"
	create_dir(results_dir)
	postcount_dir = create_dir(results_dir, "post_count_stats")
	for cat, cat_results in count_dic.items():
		cat_dir = create_dir(postcount_dir, cat)
		stat_chat_gen_count_recursion(
			cat_results, cat_dir, cat_step=extra_step_per_cat[cat]
		)


def stat_chat_gen_count_recursion(
	dic, dir, cat_step=0, remain_steps=-1, sort_by=None
):
	for key, value in dic.items():
		if remain_steps == 0:
			stat_chat_gen_count_final(key, value, dir, sort_by)
			continue
		new_dir = create_dir(dir, key)
		if "sorted_by" in key:
			stat_chat_gen_count_recursion(
				value, new_dir, remain_steps=cat_step, sort_by=key
			)
		else:
			stat_chat_gen_count_recursion(
				value, new_dir, cat_step, (remain_steps - 1), sort_by
			)


# TODO: Find a way to display the longest posts and/or the most random
# posts?
def stat_chat_gen_count_final(key, dic, dir, sort_by):
	# At this point, key can either be a timeframe or a username.
	# If sort_by == "sorted_by_date", then key is a timeframe.
	# If sort_by == "sorted_by_name", then key is a username.

	# If key is a username, then we generate a line graph for that user
	# to display trends across time. If it's a timeframe, then we generate
	# a bar graph to display the top half and bottom half of the relevant stat
	# during that timeframe.
	stat_combiner = defaultdict(lambda: {})
	new_dir = create_dir(dir, key)
	for inner_key, stat_dic in dic.items():
		if inner_key == "global":
			continue
		for stat_type, value in stat_dic.items():
			if "_only" in stat_type:
				stat_avg = "_".join([stat_type.split("_")[0], "avg"])
				stat_med = "_".join([stat_type.split("_")[0], "med"])
				stat_max = "_".join([stat_type.split("_")[0], "max"])
				stat_min = "_".join([stat_type.split("_")[0], "min"])
				stat_std = "_".join([stat_type.split("_")[0], "std"])
				stat_combiner[stat_avg][inner_key] = value[1]
				stat_combiner[stat_med][inner_key] = value[1]
				stat_combiner[stat_max][inner_key] = value[1]
				stat_combiner[stat_min][inner_key] = value[1]
				stat_combiner[stat_std][inner_key] = value[1]
			else:
				if isinstance(value, (int, float)):
					stat_combiner[stat_type][inner_key] = value
				else:
					stat_combiner[stat_type][inner_key] = value[1]

	for stat_type, stat_dic in stat_combiner.items():
		file_name = os.path.join(new_dir, stat_type + ".png")
		if "date" in sort_by:
			stats_sorted = sorted(
				stat_dic.items(), key=lambda val: val[1], reverse=True
			)
			names = [pair[0] for pair in stats_sorted]
			stat_vals = [pair[1] for pair in stats_sorted]
			color1 = ['red'] * int(len(names) / 2)
			color2 = ['blue'] * (len(names) - int(len(names) / 2))
			color = color1 + color2
			# If we have more than 20 users, cut them into top 10 and bottom
			# 10 for the category in question.
			if len(names) > 20:
				names = names[:10] + ["..."] + names[-10:]
				stat_vals = stat_vals[:10] + [0] + stat_vals[-10:]
				color1 = ['red'] * 10
				color2 = ['blue'] * 10
				color[11] = 'white'
			plt.xticks(rotation=90)
			plt.gcf().subplots_adjust(bottom=0.4)
			plt.bar(names, stat_vals, color=color)
			plt.savefig(file_name)
			plt.clf()
		else:
			time_per = stat_dic.keys()
			stat_vals = stat_dic.values()
			plt.xticks(rotation=90)
			plt.gcf().subplots_adjust(bottom=0.25)
			plt.plot(time_per, stat_vals)
			plt.title(key)
			plt.xlabel(stat_type)
			plt.ylabel('value')
			plt.savefig(file_name)
			plt.clf()


def create_dir(path, addn_path=None):
	if addn_path is not None:
		path = os.path.join(path, addn_path)
	if not os.path.exists(path):
		os.mkdir(path)
	return path
