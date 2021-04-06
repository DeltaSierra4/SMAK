from collections import defaultdict

import textacy
import textacy.ke

import strprocutil

"""
	Post analyzer module for the Social Media Analytics Kit.
	The brain of the Social Media Analytics Kit, this module reads through
	all posts and performs NLP analysis such as key term extraction, word
	statistics, and sentiment detection.

	@author: DeltaSierra4
"""


def analyze_comments(comm_dic, en, username):
	return_dic = {
		"monthly_url_count": defaultdict(lambda: defaultdict(lambda: 0)),
		"monthly_wordcloud": defaultdict(
			lambda: defaultdict(lambda: defaultdict(lambda: 0))
		),
		"monthly_sgrank": defaultdict(lambda: defaultdict(lambda: 0)),
		"monthly_textrank": defaultdict(lambda: defaultdict(lambda: 0)),
		"monthly_statistics": defaultdict(lambda: defaultdict(lambda: [])),
		"monthly_wordcloud_hl": defaultdict(lambda: defaultdict(lambda: 0)),
		"monthly_sgrank_hl": defaultdict(lambda: defaultdict(lambda: 0)),
		"monthly_textrank_hl": defaultdict(lambda: defaultdict(lambda: 0))
	}

	for g, gset in comm_dic.items():
		for target, pset in gset.items():
			if target == "Own":
				analyze_comments_helper(pset, username, en, return_dic)
			else:
				for name, person_posts in pset.items():
					analyze_comments_helper(person_posts, name, en, return_dic)
	return return_dic


"""
	Extension of the analyze_comments() above for clarity.

	Steps of this function:
	1. Extract URLs and headlines (if any) from those URLS. Pool those URLs
	and headlines together in a monthly dictionary for later analysis.
	2. Obtain a list of posts with said URLs and long words pruned out.
	3. Obtain a wordcount per user per month (do not count stopwords or
	symbols, punctuations, and emoji for this step. All words must be
	lower-case)
	4. Obtain keywords per month (keyword per user feature is not supported yet)
	5. Obtain relevant statistical values in monthly format (so that monthly
	averages and global averages can be computed at the very end).
	6. Repeat the above for monthly headlines.
	7. Return the results dictionary.
"""


def analyze_comments_helper(comm_dic, name, en, r_dic):
	news_headlines_monthly = defaultdict(lambda: [])
	for year, annual_posts in comm_dic.items():
		for month, monthly_posts in annual_posts.items():
			y_m_str = str(year) + "-"
			if int(month) < 10:
				y_m_str += ("0" + str(month))
			else:
				y_m_str += str(month)
			for _, daily_posts in monthly_posts.items():
				for _, post_list in daily_posts.items():
					# Step 1
					url_dic, headlines, posts = strprocutil.extract_urls(post_list, False)
					news_headlines_monthly[y_m_str] += headlines
					for url, count in url_dic.items():
						r_dic["monthly_url_count"][y_m_str][url] += count
					# Step 2
					preproc_posts = strprocutil.preproc_posts(posts)
					# Step 3
					only_legit_words = strprocutil.wordcloud_preproc(preproc_posts, True)
					wordcount_generator(
						only_legit_words, r_dic["monthly_wordcloud"], name, y_m_str
					)
					# Steps 4 & 5
					keyterm_stats_generator(
						preproc_posts, en, r_dic["monthly_sgrank"],
						r_dic["monthly_textrank"], r_dic["monthly_statistics"], y_m_str
					)
	# Step 6
	for month, headlines in news_headlines_monthly.items():
		only_legit_words_hl = strprocutil.wordcloud_preproc(headlines, False)
		wordcount_generator(
			only_legit_words_hl, r_dic["monthly_wordcloud_hl"], None, month
		)
		keyterm_stats_generator(
			headlines, en, r_dic["monthly_sgrank_hl"], r_dic["monthly_textrank_hl"],
			None, month
		)


"""
	Steps of this function:
	1. Extract URLs and headlines (if any) from those URLS. Pool those URLs
	and headlines together in a monthly dictionary for later analysis.
	2. Obtain a list of posts with said URLs and long words pruned out.
	3. Obtain a wordcount per user per month (do not count stopwords or
	symbols, punctuations, and emoji for this step. All words must be
	lower-case)
	4. Obtain keywords per month (keyword per user feature is not supported yet)
	5. Obtain relevant statistical values in monthly format (so that monthly
	averages and global averages can be computed at the very end).
	6. Repeat the above for monthly headlines.
	7. Return the results dictionary.
"""


def analyze_posts(post_dic, en, username=""):
	# URLs don't need to be divided by usernames, but wordclouds do.
	url_count_monthly = defaultdict(lambda: defaultdict(lambda: 0))
	news_headlines_monthly = defaultdict(lambda: [])
	monthly_wordcloud = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(lambda: 0)
		)
	)
	monthly_sgrank = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_textrank = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_statistics = defaultdict(lambda: defaultdict(lambda: []))
	# Same data as above but only for news headlines
	monthly_wordcloud_hl = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_sgrank_hl = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_textrank_hl = defaultdict(lambda: defaultdict(lambda: 0))

	for name, person_posts in post_dic.items():
		for year, annual_posts in person_posts.items():
			for month, monthly_posts in annual_posts.items():
				y_m_str = str(year) + "-"
				if int(month) < 10:
					y_m_str += ("0" + str(month))
				else:
					y_m_str += str(month)
				for _, daily_posts in monthly_posts.items():
					for _, post_list in daily_posts.items():
						# Step 1
						url_dic, headlines, posts = strprocutil.extract_urls(post_list, False)
						news_headlines_monthly[y_m_str] += headlines
						for url, count in url_dic.items():
							url_count_monthly[y_m_str][url] += count
						# Step 2
						preproc_posts = strprocutil.preproc_posts(posts)
						# Step 3
						only_legit_words = strprocutil.wordcloud_preproc(preproc_posts, True)
						wordcount_generator(only_legit_words, monthly_wordcloud, name, y_m_str)
						# Steps 4 & 5
						keyterm_stats_generator(
							preproc_posts, en, monthly_sgrank, monthly_textrank,
							monthly_statistics, y_m_str
						)
	# Step 6
	for month, headlines in news_headlines_monthly.items():
		only_legit_words_hl = strprocutil.wordcloud_preproc(headlines, False)
		wordcount_generator(only_legit_words_hl, monthly_wordcloud_hl, None, month)
		keyterm_stats_generator(
			headlines, en, monthly_sgrank_hl, monthly_textrank_hl,
			None, month
		)
	# Step 7
	return collect_results(
		url_count_monthly, monthly_wordcloud, monthly_sgrank, monthly_textrank,
		monthly_statistics, monthly_wordcloud_hl, monthly_sgrank_hl,
		monthly_textrank_hl
	)


"""
	Steps of this function:
	1. Extract URLs and headlines (if any) from those URLS. Pool those URLs
	and headlines together in a monthly dictionary for later analysis.
	2. Obtain a list of posts with said URLs and long words pruned out.
	3. Obtain a wordcount per user per month (do not count stopwords or
	symbols, punctuations, and emoji for this step. All words must be
	lower-case)
	4. Obtain keywords per month (keyword per user feature is not supported yet)
	5. Obtain relevant statistical values in monthly format (so that monthly
	averages and global averages can be computed at the very end).
	6. Repeat the above for monthly headlines.
	7. Return the results dictionary.
"""


def analyze_messages(mess_dic, en, username=""):
	# URLs don't need to be divided by usernames, but wordclouds do.
	url_count_monthly = defaultdict(lambda: defaultdict(lambda: 0))
	news_headlines_monthly = defaultdict(lambda: [])
	monthly_wordcloud = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(lambda: 0)
		)
	)
	monthly_sgrank = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_textrank = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_statistics = defaultdict(lambda: defaultdict(lambda: []))
	# Same data as above but only for news headlines
	monthly_wordcloud_hl = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_sgrank_hl = defaultdict(lambda: defaultdict(lambda: 0))
	monthly_textrank_hl = defaultdict(lambda: defaultdict(lambda: 0))

	for g, gset in mess_dic.items():
		for name, person_posts in gset.items():
			for year, annual_posts in person_posts.items():
				for month, monthly_posts in annual_posts.items():
					y_m_str = str(year) + "-"
					if int(month) < 10:
						y_m_str += ("0" + str(month))
					else:
						y_m_str += str(month)
					for _, daily_posts in monthly_posts.items():
						for _, post_list in daily_posts.items():
							# Step 1
							url_dic, headlines, posts = strprocutil.extract_urls(post_list, False)
							news_headlines_monthly[y_m_str] += headlines
							for url, count in url_dic.items():
								url_count_monthly[y_m_str][url] += count
							# Step 2
							preproc_posts = strprocutil.preproc_posts(posts)
							# Step 3
							only_legit_words = strprocutil.wordcloud_preproc(preproc_posts, True)
							wordcount_generator(only_legit_words, monthly_wordcloud, name, y_m_str)
							# Steps 4 & 5
							keyterm_stats_generator(
								preproc_posts, en, monthly_sgrank, monthly_textrank,
								monthly_statistics, y_m_str
							)
	# Step 6
	for month, headlines in news_headlines_monthly.items():
		only_legit_words_hl = strprocutil.wordcloud_preproc(headlines, False)
		wordcount_generator(only_legit_words_hl, monthly_wordcloud_hl, None, month)
		keyterm_stats_generator(
			headlines, en, monthly_sgrank_hl, monthly_textrank_hl,
			None, month
		)
	# Step 7
	return collect_results(
		url_count_monthly, monthly_wordcloud, monthly_sgrank, monthly_textrank,
		monthly_statistics, monthly_wordcloud_hl, monthly_sgrank_hl,
		monthly_textrank_hl
	)


def count_comments(comm_dic, en, username=""):
	post_count_res_date = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(lambda: defaultdict(lambda: {}))
		)
	)
	post_count_res_name = defaultdict(
		lambda: defaultdict(
			lambda: defaultdict(lambda: defaultdict(lambda: {}))
		)
	)
	return_dic = {
		"sorted_by_date": post_count_res_date,
		"sorted_by_name": post_count_res_name,
	}
	for g, gset in comm_dic.items():
		for target, pset in gset.items():
			if target == "Own":
				count_comments_helper(
					pset, en, return_dic, username, g
				)
			else:
				for name, person_posts in pset.items():
					count_comments_helper(
						person_posts, en, return_dic, name, g, t=target
					)
	return return_dic


"""
	Extension of the analyze_comments() above for clarity.

	Steps of this function:
	1. Extract URLs and headlines (if any) from those URLS. Pool those URLs
	and headlines together in a monthly dictionary for later analysis.
	2. Obtain a list of posts with said URLs and long words pruned out.
	3. Obtain a wordcount per user per month (do not count stopwords or
	symbols, punctuations, and emoji for this step. All words must be
	lower-case)
	4. Obtain keywords per month (keyword per user feature is not supported yet)
	5. Obtain relevant statistical values in monthly format (so that monthly
	averages and global averages can be computed at the very end).
	6. Repeat the above for monthly headlines.
	7. Return the results dictionary.
"""


def count_comments_helper(comm_dic, en, r_dic, name, group, t=None):
	if t == "Replies":
		tstr = t
	else:
		tstr = "Comments"
	for year, annual_posts in comm_dic.items():
		for month, monthly_posts in annual_posts.items():
			y_m_str = str(year) + "-"
			if int(month) < 10:
				y_m_str += ("0" + str(month))
			else:
				y_m_str += str(month)
			for _, daily_posts in monthly_posts.items():
				for _, post_list in daily_posts.items():
					if group == "NonGroup":
						gstrs = group
					else:
						gstrs = [p.get("Group name", "Other Group") for p in post_list]
					_, _, posts = strprocutil.extract_urls(post_list, True)
					count_stats_generator(
						posts, en, r_dic["sorted_by_date"], r_dic["sorted_by_name"],
						len(post_list), y_m_str, name, g_name=gstrs, t_name=tstr
					)


"""
	Returns two dictionaries - one ordered by date, another ordered by username.
	First, remove urls and preprocess text, then simply count number of posts
	and do very basic statistics generation such as word count, character count,
	or even sentiment detection.
"""


def count_posts(post_dic, en, username=""):
	post_count_res_date = defaultdict(lambda: defaultdict(lambda: {}))
	post_count_res_name = defaultdict(lambda: defaultdict(lambda: {}))
	for name, person_posts in post_dic.items():
		for year, annual_posts in person_posts.items():
			for month, monthly_posts in annual_posts.items():
				y_m_str = str(year) + "-"
				if int(month) < 10:
					y_m_str += ("0" + str(month))
				else:
					y_m_str += str(month)
				for _, daily_posts in monthly_posts.items():
					for _, post_list in daily_posts.items():
						_, _, posts = strprocutil.extract_urls(post_list, False)
						count_stats_generator(
							posts, en, post_count_res_date, post_count_res_name,
							len(post_list), y_m_str, name
						)
	return {
		"sorted_by_date": post_count_res_date,
		"sorted_by_name": post_count_res_name,
	}


"""
	Returns two dictionaries - one ordered by date, another ordered by username.
	Both dictionaries will separate results between group messages and individual
	messages. First, remove urls and preprocess text, then simply count number
	of posts and do very basic statistics generation such as word count, character
	count, or even sentiment detection.
"""


def count_messages(mess_dic, en, username=""):
	post_count_res_date = defaultdict(
		lambda: defaultdict(lambda: defaultdict(lambda: {}))
	)
	post_count_res_name = defaultdict(
		lambda: defaultdict(lambda: defaultdict(lambda: {}))
	)
	for g, gset in mess_dic.items():
		for name, person_posts in gset.items():
			for year, annual_posts in person_posts.items():
				for month, monthly_posts in annual_posts.items():
					y_m_str = str(year) + "-"
					if int(month) < 10:
						y_m_str += ("0" + str(month))
					else:
						y_m_str += str(month)
					for _, daily_posts in monthly_posts.items():
						for _, post_list in daily_posts.items():
							_, _, posts = strprocutil.extract_urls(post_list, False)
							count_stats_generator(
								posts, en, post_count_res_date, post_count_res_name,
								len(post_list), y_m_str, name, isgroup=g
							)
	return {
		"sorted_by_date": post_count_res_date,
		"sorted_by_name": post_count_res_name,
	}


SUB_DIRECTORIES_FUNC_ANALYZE = {
	"comments": analyze_comments,
	"messages": analyze_messages,
	"posts": analyze_posts,
}

SUB_DIRECTORIES_FUNC_COUNT = {
	"comments": count_comments,
	"messages": count_messages,
	"posts": count_posts,
}


"""
	analyze() through all posts contained in the master_dic. Further divided
	into analyze_comments(), analyze_posts(), and analyze_messages()
"""


def analyze(master_dic, username):
	en = textacy.load_spacy_lang("en_core_web_sm", disable=("parser",))
	result_dic = {}
	for sub in SUB_DIRECTORIES_FUNC_ANALYZE.keys():
		print("Analyzing directory", sub)
		result_dic[sub] = SUB_DIRECTORIES_FUNC_ANALYZE[sub](
			master_dic[sub], en, username
		)
	return result_dic


"""
	Parse through master_dic to do basic post counting and/or basic word-related
	statistics analysis for each entity interacted with. Returns a dictionary
	with data such as person whom the user interacted with the most in a given
	month, user with most word/character count, or global statistics across
	all users in a group, etc. All results are sorted by year-month units.

	TODO: Future implement - sentiment detection.
"""


def post_counts(master_dic, username, sub_directories):
	en = textacy.load_spacy_lang("en_core_web_sm", disable=("parser",))
	result_dic = {}
	for sub in SUB_DIRECTORIES_FUNC_COUNT.keys():
		print("Counting in directory", sub)
		result_dic[sub] = SUB_DIRECTORIES_FUNC_COUNT[sub](
			master_dic[sub], en, username
		)
	return result_dic


"""
	Helper method to generate word count in a list of posts.
"""


def wordcount_generator(posts, monthly_wordcloud, name, y_m_str):
	for post in posts:
		wordlist = post.split()
		wordset = set(wordlist)
		for individual_word in wordset:
			if name is not None:
				monthly_wordcloud[name][y_m_str][individual_word] += \
					wordlist.count(individual_word)
			else:
				monthly_wordcloud[y_m_str][individual_word] += \
					wordlist.count(individual_word)


"""
	Helper method to collect key terms from a list of posts

	TODO! Maybe implement a way for the user to fine-tune all these options?
	Hint: Use a dictionary to pass in the parameters, just like spacy's config
	system.
"""


def keyterm_stats_generator(
	posts, en, monthly_sgrank, monthly_textrank, monthly_statistics, y_m_str
):
	stopword_list = strprocutil.load_stopwords()
	for i in range(len(posts)):
		post = posts[i]
		# Use only lower case for keyterm extraction. Leave case alone for
		# everything else.
		curdoc = textacy.make_spacy_doc(post.lower(), lang=en)
		curdoc_kt = textacy.make_spacy_doc(post, lang=en)
		curdoc_ranks_sg = textacy.ke.sgrank(
			curdoc_kt, ngrams=(1, 2, 3, 4), normalize="lower", topn=0.3
		)
		curdoc_ranks_tr = textacy.ke.textrank(
			curdoc_kt, normalize="lower", topn=0.3
		)
		for word in curdoc_ranks_sg:
			if word[0] not in stopword_list:
				monthly_sgrank[y_m_str][word[0]] += 1
		for word in curdoc_ranks_tr:
			if word[0] not in stopword_list:
				monthly_textrank[y_m_str][word[0]] += 1

		if monthly_statistics is None:
			continue

		ts = textacy.TextStats(curdoc)
		monthly_statistics[y_m_str]["wordcount"].append((post, ts.n_words))
		monthly_statistics[y_m_str]["sylcount"].append((post, ts.n_syllables))
		monthly_statistics[y_m_str]["charcount"].append((post, len(post)))
		monthly_statistics[y_m_str]["entropy"].append((post, ts.entropy))

		meaningful_words = strprocutil.gibberishremove(post)
		newdoc = textacy.make_spacy_doc(meaningful_words.lower(), lang=en)
		ns = textacy.TextStats(newdoc)
		if len(newdoc) > 2:
			# These statistics are only meaningful on longer sentences.
			try:
				monthly_statistics[y_m_str]["fkgl"].append(
					(post, ns.flesch_kincaid_grade_level)
				)
			except ZeroDivisionError:
				pass
			try:
				monthly_statistics[y_m_str]["fre"].append(
					(post, ns.flesch_reading_ease)
				)
			except ZeroDivisionError:
				pass
			try:
				monthly_statistics[y_m_str]["clix"].append(
					(post, ns.coleman_liau_index)
				)
			except ZeroDivisionError:
				pass
			try:
				monthly_statistics[y_m_str]["lixl"].append((post, ns.lix))
			except ZeroDivisionError:
				pass


"""
	Similar to the keyterm_stats_generator() method above, this is a helper
	method to collect basic count stats from a list of posts.
"""


def count_stats_generator(
	posts_all, en, count_date, count_name, post_count, y_m_str, name,
	isgroup=None, g_name=None, t_name=None
):
	if g_name is None or isinstance(g_name, str):
		posts = [p for p in posts_all if len(p) > 0]
		if isgroup is not None:
			order_by_date = count_date[isgroup][y_m_str][name]
			order_by_name = count_name[isgroup][name][y_m_str]
		elif g_name is not None:
			# t_name will always have a value if g_name is assigned
			order_by_date = count_date[g_name][t_name][y_m_str][name]
			order_by_name = count_name[g_name][t_name][name][y_m_str]
		else:
			order_by_date = count_date[y_m_str][name]
			order_by_name = count_name[name][y_m_str]

		order_by_date["count"] = order_by_date.get("count", 0) + post_count
		order_by_name["count"] = order_by_name.get("count", 0) + post_count
		order_by_date["stats"] = order_by_date.get("stats", defaultdict(lambda: []))
		order_by_name["stats"] = order_by_name.get("stats", defaultdict(lambda: []))
		for post in posts:
			curdoc = textacy.make_spacy_doc(post, lang=en)
			ts = textacy.TextStats(curdoc)
			wc = (post, ts.n_words)
			cc = (post, len(post))
			ey = (post, ts.entropy)
			order_by_date["stats"]["wordcount"].append(wc)
			order_by_date["stats"]["charcount"].append(cc)
			order_by_date["stats"]["entropy"].append(ey)
			order_by_name["stats"]["wordcount"].append(wc)
			order_by_name["stats"]["charcount"].append(cc)
			order_by_name["stats"]["entropy"].append(ey)

	else:
		# g_name is in the form of a list. We'll need to carefully sort through
		# group names.
		for id in range(len(posts_all)):
			post = posts_all[id]
			g_name_str = g_name[id]
			order_by_date = count_date[g_name_str][t_name][y_m_str][name]
			order_by_name = count_name[g_name_str][t_name][name][y_m_str]
			order_by_date["count"] = order_by_date.get("count", 0) + 1
			order_by_name["count"] = order_by_name.get("count", 0) + 1
			order_by_date["stats"] = order_by_date.get("stats", defaultdict(lambda: []))
			order_by_name["stats"] = order_by_name.get("stats", defaultdict(lambda: []))
			curdoc = textacy.make_spacy_doc(post, lang=en)
			ts = textacy.TextStats(curdoc)
			wc = (post, ts.n_words)
			cc = (post, len(post))
			ey = (post, ts.entropy)
			order_by_date["stats"]["wordcount"].append(wc)
			order_by_date["stats"]["charcount"].append(cc)
			order_by_date["stats"]["entropy"].append(ey)
			order_by_name["stats"]["wordcount"].append(wc)
			order_by_name["stats"]["charcount"].append(cc)
			order_by_name["stats"]["entropy"].append(ey)


"""
	collect_results() to be returned by each analyze() functions. Simply checks
	if each dictionary is not empty and adds it to the return dictionary if it
	isn't.
"""


def collect_results(
	url_count_monthly, monthly_wordcloud, monthly_sgrank, monthly_textrank,
	monthly_statistics, monthly_wordcloud_hl, monthly_sgrank_hl,
	monthly_textrank_hl
):
	return_dic = {}
	if len(url_count_monthly.keys()) > 0:
		return_dic["monthly_url_count"] = url_count_monthly
	if len(monthly_wordcloud.keys()) > 0:
		return_dic["monthly_wordcloud"] = monthly_wordcloud
	if len(monthly_sgrank.keys()) > 0:
		return_dic["monthly_sgrank"] = monthly_sgrank
	if len(monthly_textrank.keys()) > 0:
		return_dic["monthly_textrank"] = monthly_textrank
	if len(monthly_statistics.keys()) > 0:
		return_dic["monthly_statistics"] = monthly_statistics
	if len(monthly_wordcloud_hl.keys()) > 0:
		return_dic["monthly_wordcloud_hl"] = monthly_wordcloud_hl
	if len(monthly_sgrank_hl.keys()) > 0:
		return_dic["monthly_sgrank_hl"] = monthly_sgrank_hl
	if len(monthly_textrank_hl.keys()) > 0:
		return_dic["monthly_textrank_hl"] = monthly_textrank_hl
	return return_dic
