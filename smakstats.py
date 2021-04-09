from collections import defaultdict
from statistics import mean, median, stdev

"""
	Statistics module for Social Media Analytics Kit.
	Parses through the results dictionary and produces an output readable for
	the human eye. Also creates a JSON to be used for wordcloud generation
	or display of graphs.

	@author: DeltaSierra4
"""


def parse_results(result_dic, subdirectories):
	res_dic = {
		"monthly_cat": {},
		"annual_cat": {},
		"global_cat": {},
		"monthly_cross": {},
		"annual_cross": {},
		"global_cross": {},
	}
	keys = [
		"_url_count",
		"_wordcloud",
		"_sgrank",
		"_textrank",
		"_statistics",
		"_wordcloud_hl",
		"_sgrank_hl",
		"_textrank_hl",
	]
	periods = list(set([key.split("_")[0] for key in res_dic.keys()]))
	for sub in subdirectories:
		for per in periods:
			res_dic[(per + "_cat")][sub] = parse_results_helper(
				result_dic[sub], per, keys, False
			)
	for per in periods:
		res_dic[(per + "_cross")] = parse_results_helper(result_dic, per, keys, True)
	return res_dic


"""
	Parse through results dictionary for all stats across each subdirectory
	for each period.

	per == "monthly" for monthly stats, "annual" for yearly stats, and "global"
	for global stats

	is_cross == True if stats are to be aggregated across all sub-categories,
	False otherwise.
"""


def parse_results_helper(result_dic, per, keys, is_cross):
	combine_dic = {}
	res_dic = {}
	for key in keys:
		pk = per + key
		if "statistics" in key:
			combine_dic[pk] = defaultdict(lambda: defaultdict(lambda: []))
			res_dic[pk] = defaultdict(lambda: {})
		else:
			combine_dic[pk] = defaultdict(lambda: defaultdict(lambda: 0))
			res_dic[pk] = defaultdict(lambda: [])
	wordcloud_com_user = defaultdict(
		lambda: defaultdict(lambda: defaultdict(lambda: 0))
	)

	# Step 1
	if is_cross:
		for _, dic in result_dic.items():
			combiner(dic, per, combine_dic, wordcloud_com_user)
	else:
		combiner(result_dic, per, combine_dic, wordcloud_com_user)

	# Step 2
	stat_analysis(combine_dic, wordcloud_com_user, res_dic, per)
	return res_dic


"""
	Helper method to aggregate all results from the postanalyzer module.
"""


def combiner(result_dic, per, combine_dic, wordcloud_com_user):
	for k, sub_dic in result_dic.items():
		new_k = "_".join([per] + k.split("_")[1:])
		if "_hl" in k or "wordcloud" not in k:
			# Combine word counts for everthing except normal wordcloud
			for month, month_dic in sub_dic.items():
				pk = month
				if per == "annual":
					pk = month.split("-")[0]
				elif per == "global":
					pk = per
				for term, count in month_dic.items():
					combine_dic[new_k][pk][term] += count
		else:
			# Combine word counts for wordcloud only
			for name, person_posts in sub_dic.items():
				for month, month_dic in person_posts.items():
					pk = month
					if per == "annual":
						pk = month.split("-")[0]
					elif per == "global":
						pk = per
					for term, count in month_dic.items():
						combine_dic[new_k][pk][term] += count
						wordcloud_com_user[name][pk][term] += count


"""
	Helper method to analyze all aggregated results from combiner().
"""


def stat_analysis(combine_dic, wordcloud_com_user, res_dic, per):
	for k, sub_dic in combine_dic.items():
		for t, t_dic in sub_dic.items():
			if "statistics" not in k:
				terms_sorted = sorted(
					t_dic.items(), key=lambda val: val[1], reverse=True
				)
				if "rank" in k:
					terms_sorted = terms_sorted[:100]
				elif "wordcloud" in k:
					terms_sorted = terms_sorted[:500]
				res_dic[k][t] = terms_sorted
			else:
				for stat_type, stat_list in t_dic.items():
					stat_num_only = [score[1] for score in stat_list]
					stat_sorted = sorted(stat_list, key=lambda val: val[1], reverse=True)
					if len(stat_num_only) > 1:
						res_dic[k][t][(stat_type + "_avg")] = mean(stat_num_only)
						res_dic[k][t][(stat_type + "_med")] = median(stat_num_only)
						res_dic[k][t][(stat_type + "_std")] = stdev(stat_num_only)
						res_dic[k][t][(stat_type + "_max")] = stat_sorted[0]
						res_dic[k][t][(stat_type + "_min")] = stat_sorted[-1]
					else:
						res_dic[k][t][(stat_type + "_only")] = stat_sorted[0]

	wordcloud_per_user = defaultdict(lambda: defaultdict(lambda: []))
	for name, dic in wordcloud_com_user.items():
		for t, wc in dic.items():
			wordcloud_per_user[name][t] = sorted(
				wc.items(), key=lambda val: val[1], reverse=True
			)[:500]
	res_dic[per + "_wordcloud_users"] = wordcloud_per_user


def parse_counts_comments(count_dic, per=None):
	agg_result_dic = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(
				lambda: defaultdict(
					lambda: defaultdict(
						lambda: defaultdict(
							lambda: 0
						)
					)
				)
			)
		)
	)
	aggregate_counts_recursive(count_dic, agg_result_dic, per)
	result_dic = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(
				lambda: defaultdict(
					lambda: defaultdict(
						lambda: defaultdict(
							lambda: 0
						)
					)
				)
			)
		)
	)
	stats_counts_recursive(agg_result_dic, result_dic)
	return result_dic


def parse_counts_messages(count_dic, per=None):
	agg_result_dic = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(
				lambda: defaultdict(
					lambda: defaultdict(
						lambda: 0
					)
				)
			)
		)
	)
	aggregate_counts_recursive(count_dic, agg_result_dic, per)
	result_dic = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(
				lambda: defaultdict(
					lambda: defaultdict(
						lambda: 0
					)
				)
			)
		)
	)
	stats_counts_recursive(agg_result_dic, result_dic)
	return result_dic


def parse_counts_posts(count_dic, per=None):
	agg_result_dic = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(
				lambda: defaultdict(
					lambda: 0
				)
			)
		)
	)
	aggregate_counts_recursive(count_dic, agg_result_dic, per)
	result_dic = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(
				lambda: defaultdict(
					lambda: 0
				)
			)
		)
	)
	stats_counts_recursive(agg_result_dic, result_dic)
	return result_dic


PARSE_FUNC = {
	"comments": parse_counts_comments,
	"messages": parse_counts_messages,
	"posts": parse_counts_posts
}


def parse_counts(count_dic, subdirectories):
	result_dic = defaultdict(
		lambda: defaultdict(
			lambda: {}
		)
	)
	per = ["monthly", "annual", "global"]
	for sub in subdirectories:
		for p in per:
			if p != "monthly":
				result_dic[sub][p] = PARSE_FUNC[sub](count_dic[sub], p)
			else:
				result_dic[sub][p] = PARSE_FUNC[sub](count_dic[sub])
	return result_dic


def aggregate_counts_recursive(dic, res_dic, per=None):
	for k, v in dic.items():
		if "count" not in dic.keys():
			new_k = k
			# Check if dates are in this dictionary. If so, pool results here.
			key_date = dic.keys()
			is_date = True
			for key in key_date:
				date = key.split("-")
				if not (len(date) == 2 and date[0].isdigit() and date[1].isdigit()):
					# We are not in the date layer yet
					is_date = False
					break
			if is_date:
				# We have found the layer containing dates.
				if per == "annual":
					new_k = date[0]
				elif per == "global":
					new_k = per
			aggregate_counts_recursive(v, res_dic[new_k], per)
		elif k == "count":
			res_dic[k] = res_dic.get(k, 0) + v
		else:
			for k_stats, stats in v.items():
				res_dic[k_stats] = res_dic.get(k_stats, []) + stats


def stats_counts_recursive(dic, res_dic):
	for k, v in dic.items():
		if "count" not in dic.keys():
			stats_counts_recursive(v, res_dic[k])
		elif k != "count":
			stat_num_only = [score[1] for score in v]
			stat_sorted = sorted(v, key=lambda val: val[1], reverse=True)
			if len(stat_num_only) > 1:
				res_dic[(k + "_avg")] = mean(stat_num_only)
				res_dic[(k + "_med")] = median(stat_num_only)
				res_dic[(k + "_std")] = stdev(stat_num_only)
				res_dic[(k + "_max")] = stat_sorted[0]
				res_dic[(k + "_min")] = stat_sorted[-1]
			else:
				res_dic[(k + "_only")] = stat_sorted[0]
		else:
			res_dic[k] = v
