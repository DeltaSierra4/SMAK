from collections import defaultdict
import re

from textacy import preprocessing

"""
	String processor utility module for the Social Media Analytics Kit.
	Performs various string processing functions for loading data and
	preprocessing before analysis is performed.

	@author: DeltaSierra4
"""


"""
	Comprehensive convert_str() that performs all conversions in the following
	order:

	1. Conversion of incorrect unicode characters into UTF-8-like characters.
	2. Conversion of name tags into actual names without the numbers and the
	tag symbol.
"""


def convert_str(input_str):
	after_unicode = convert_unicode(input_str)
	after_name_tag_conv = convert_name_tag(after_unicode)
	return after_name_tag_conv.strip()


"""
	Convert any incorrectly expressed unicode characters into UTF-8-like
	characters using regex. Returns the converted string (or the original
	string if there are no unicode expressions).
"""


def convert_unicode(input_str):
	return re.sub(
		r'[\xc2-\xf4][\x80-\xbf]+',
		lambda m: m.group(0).encode('latin1').decode('utf8'),
		input_str
	)


"""
	Convert any name tags expressed in posts and comments as original names.

	input: @[123456789:1234:John Doe] pay for my Pizza.
	output: John Doe pay for my Pizza.
"""


def convert_name_tag(input_str):
	name_tags = re.findall(r'\@\[[0-9]+\:[0-9]+\:[A-Za-z0-9 ]+\]', input_str)
	actual_names = [nt.split(":")[2][:-1] for nt in name_tags]
	for i in range(len(name_tags)):
		input_str = input_str.replace(name_tags[i], actual_names[i])
	return input_str


"""
	Remove gibberish from a given string and returns it. This is anything like
	";w;", bunches of punctuation marks, or emoji-only posts. We also check for
	single-word posts that don't really mean much.
"""


def gibberishremove(inputstring):
	remove_email = preprocessing.replace_numbers(
		inputstring.strip(), replace_with=""
	).strip()
	remove_phone = preprocessing.replace_phone_numbers(
		remove_email, replace_with=""
	).strip()
	remove_cur = preprocessing.replace_currency_symbols(
		remove_phone.strip(), replace_with=""
	).strip()
	removal_symbols = "+=-_?!/\\:;\"'@#$%^&*()[]{}<>~"
	remove_sym = preprocessing.remove_punctuation(
		remove_cur, marks=removal_symbols
	).strip()
	remove_num = preprocessing.replace_numbers(
		remove_sym, replace_with=""
	).strip()
	outputstring = preprocessing.replace_emojis(
		remove_num, replace_with=""
	).strip()
	return outputstring


"""
	Check if a given string contains phone numbers or emails.
	Then it checks if said string only contains numbers, emojis, or symbols.
"""


def number_and_punccheck(inputstr):
	remove_phone = preprocessing.replace_phone_numbers(
		inputstr, replace_with=""
	)
	if inputstr != remove_phone:
		return True

	remove_email = preprocessing.replace_numbers(
		inputstr, replace_with=""
	)
	if inputstr != remove_email:
		return True

	remove_cur = preprocessing.replace_currency_symbols(
		inputstr.strip(), replace_with=""
	).strip()
	removal_symbols = "+=-_?!/\\:;\"'@#$%^&*()[]{}<>~"
	remove_sym = preprocessing.remove_punctuation(
		remove_cur, marks=removal_symbols
	).strip()
	remove_num = preprocessing.replace_numbers(
		remove_sym, replace_with=""
	).strip()
	remove_emo = preprocessing.replace_emojis(
		remove_num, replace_with=""
	).strip()
	return remove_emo == ""


"""
	extract_urls() from a given post list. Returns a dictionary of counts of URL
	hostnames, a list of headlines, if the URL is a news article with headline
	data available, and a list of posts in a dictionary format with the URLs
	removed.

	keep_empties == True IFF this function is being called from the basic stats
	counter that needs to keep track of indices of posts correctly.
"""


def extract_urls(post_list, keep_empties):
	url_count = defaultdict(lambda: 0)
	headlines = []
	posts_without_url = []
	for post_dic in post_list:
		post = post_dic["post"]

		# Regex provided by w3resource.com
		url_regex_raw = r"""
			http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|
			[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+
		"""
		url_regex = re.compile(url_regex_raw, re.VERBOSE)
		urllist = re.findall(url_regex, post)
		for url in urllist:
			orig_url = url
			if url[:8] == "https://":
				url = url[8:]
			elif url[:7] == "http://":
				url = url[7:]
			path_split = url.split("/")
			hostname = path_split[0]

			# Extract headlines if any
			headline_candidates = [
				t for t in path_split[1:] if valid_headline(t, False)
			]
			possible_hlines = []
			for t in headline_candidates:
				for wrs in t.split(".html"):
					possible_hlines += [
						nht for nht in wrs.split("?") if valid_headline(nht, True)
					]

			if len(possible_hlines) > 0:
				# At this point, all entries in possible_headlines are strings
				# containing news article headlines. Now we process them while
				# pruning out nonsensical strings to the best of our ability.
				subject = ""

				# If there are two items in possible_headlines, it's not that we
				# have two headlines: Usually, the first item is a subject or topic,
				# while the second item and onwards are the headlines.
				if len(possible_hlines) > 1:
					sub_word = [
						t for t in possible_hlines[0].split("-") if (t.isalpha() or t.isdigit())
					]
					if len(sub_word) > 0:
						subject = " ".join(sub_word)
					# The rest of the items should be headlines
					possible_hlines = possible_hlines[1:]

				# Obtain every single words in all headline items.
				comb_headline = ("-".join(possible_hlines)).split("-")
				full_headline = " ".join(
					[word for word in comb_headline if valid_hline_word(word)]
				)

				if len(subject) > 0:
					full_headline = "{}: {}".format(subject, full_headline)
				headlines.append(full_headline)

			# Occasionally, an article link will be linked to Google.
			# In this case, the article's actual hostname is inside the path
			# and will always be in the form of '[www.]xxx.com'
			if hostname == "www.google.com":
				actual_host = [l for l in headline_candidates if l[-4:] == ".com"]
				if len(actual_host) > 0:
					hostname = actual_host[0]

			# Add the hostname to the count
			url_count[hostname] += 1

			# Replace URL in the original post
			post = post.replace(orig_url, "").strip()
		if len(post) > 0 or keep_empties:
			posts_without_url.append(post)
	return url_count, headlines, posts_without_url


"""
	Helper method that checks if a given string is a possible headline for a
	news article link.

	after_html_cut == True IFF this function is being called after the split()
	on ".html"
"""


def valid_headline(s, after_html_cut):
	if not after_html_cut:
		# Headlines obviously should not be an empty string
		not_empty = (len(s) > 0)
		# Headlines have a mix of alphanumeric characters and the dash character.
		# If a string is purely alphanumeric, it is likely just a section name or
		# possibly some kind of Youtube/Facebook code?
		mixed = (not s.isalnum())
		# Headlines almost always contain more than 2 words.
		more_than_2 = (len(s.split("-")) > 2)
		# Ignore all date formats.
		not_date = (re.fullmatch(r'[0-9]+-[0-9]+-[0-9]+', s) is None)
		return (not_empty and mixed and more_than_2 and not_date)
	else:
		not_empty = (len(s) > 0)
		more_than_2 = (len(s.split("-")) > 2)
		# All article metadata contain the character "="
		not_metad = ("=" not in s and "_" not in s and "," not in s)
		return (not_empty and more_than_2 and not_metad)


"""
	Helper method that checks if a given word is a part of a headline. This
	method prunes out gibberish like UK16324894 or long numbers that are
	obviously not part of the headline. Typically, all headlines are lower
	case and do not contain numbers larger than one million.
"""


def valid_hline_word(word):
	if word.isdigit() and int(word) > 1000000:
		return False
	# An updated version of the above. Some headlines contain strings that look
	# like "n1234567"
	if word[1:].isdigit() and int(word[1:]) > 100000:
		return False
	# Next, we look for gibberish like 70e400adf209cbf52dccef47c46f9b0e i.e.
	# long hexadecimal expressions. A simple way of sifting them out is to
	# collect only the numeric portion of the string and check if it's above
	# some threshold (in this case, we set the threshold to 1000).
	if not word.isdigit():
		onlynum = "".join([dg for dg in word if dg.isdigit()])
		if len(onlynum) > 0 and int(onlynum) > 1000:
			return False
	return (word == word.lower())


"""
	Preprocess posts in a list of posts in dictionary format.

	Step 1
	Occasionally, there will be tokens that are ridiculously long. Usually
	they are tokens such as "HAHAHAHAHAHAHA", "FUCK!!!!!!!!!!!!!!!!!!!",
	"REEEEEEEEE", or "AAAAAAAAAAAAAAAAAAAAAAAAAAAA" and the such (i.e. lots
	of repeating characters or excessive punctuation marks). We cut them down
	here to smaller tokens.

	Step 2
	There are also long gibberish tokens such as "feugioawefhuawiefhwaueifhale"
	or "12343712694721364781326413287". We can't really establish a good pattern
	for those, so we simply chop those tokens down to smaller length bits, in
	units of 32 characters.
"""


def preproc_posts(posts):
	gibberish_chars = ["EE", "AA", "HA", "OO", "II", "UU"]
	gibberish_chars_lower = [exp.lower() for exp in gibberish_chars]
	gibberish_puncs = ["!!", "?!", "??", "..", ".\n"]
	preprocessed = []
	for post in posts:
		newlines = []
		lines = post.split("\n")
		for line in lines:
			longstrings_and_locs = defaultdict(lambda: [])
			words = line.split(" ")
			for ti in range(len(words)):
				if len(words[ti]) > 32:
					for exp in (gibberish_chars + gibberish_chars_lower + gibberish_puncs):
						words[ti] = preprocessing.normalize_repeating_chars(
							words[ti], chars=exp, maxn=16
						)
					if len(words[ti]) > 32:
						addn_words = []
						num_words = int(len(words[ti]) / 32)
						for mul in range(num_words + 1):
							start_ind = mul * 32
							end_ind = (mul + 1) * 32
							if end_ind > len(words[ti]):
								end_ind = len(words[ti])
							addn_words.append(words[ti][start_ind:end_ind])
						words[ti] = addn_words[0]
						longstrings_and_locs[ti] = addn_words[1:]
			if len(longstrings_and_locs.items()) > 0:
				words_added = 0
				for ti, wordlist in longstrings_and_locs.items():
					ni = ti + words_added
					words = words[:(ni + 1)] + wordlist + words[(ni + 1):]
					words_added += len(wordlist)
			newline = " ".join(words)
			newlines.append(newline)
		preproc_post = "\n".join(newlines).strip()
		if len(preproc_post) > 0:
			preprocessed.append(preproc_post)
	return preprocessed


"""
	Preprocess posts in a list of posts for the wordcloud step. Here we remove
	all punctuations, any standalone symbols or parenthetical characters, and
	convert characters into lower-case.

	is_dic == True IFF format of posts is in the form of a dictionary like:
	{
		"post": "your post"
		...
	}
"""


def wordcloud_preproc(posts, is_dic):
	pl = [
		preprocessing.remove_punctuation(p).lower().strip() for p in posts
	]
	processed_words = []
	for post in pl:
		post_words = post.split()
		post_legit_words = [w for w in post_words if not number_and_punccheck(w)]
		processed_words.append(" ".join(post_legit_words))
	return processed_words


"""
	Load a list of stopwords.
"""


def load_stopwords():
	stopwords = []
	with open('./stopwords_en.txt', 'r') as f:
		for line in f:
			stopwords.append(line.strip())
	return stopwords
