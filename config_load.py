import json
import os.path as op

"""
	Configuration loader module for Social Media Analytics Kit.
	Parses through a json file containing relevant settings for the SMAK code
	to run. Also checks through the configuration file to make sure that all
	values are legal (e.g. no negative indices in a list, Language field must
	be filled in and something that's currently supported, etc.)

	@author: DeltaSierra4
"""

#TODO! Include a portion to allow the user to select whether they want global, annual, or monthly results.

"""
	Check if all basic fields are present and are valid entries.
"""


def basic_check(config_dic):
	config_keys = config_dic.keys()
	basic_fields = [
		"Language", 
		"Username", 
		"Datadir", 
		"Resultsdir",
		"Post_types",
		"Analysis_period"
	]
	for field in basic_fields:
		try:
			assert field in config_keys
		except AssertionError:
			return {"Missing field": "Missing \"{}\" field.".format(field)}

	data_dir = config_dic["Datadir"]
	try:
		assert len(data_dir) != 0
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Datadir\" field. Provide a path to \
the folder that contains the results directory."
		}
	try:
		assert op.exists(data_dir)
	except AssertionError:
		return {"FNF": "{} is not a valid path.".format(data_dir)}

	try:
		assert len(config_dic["Resultsdir"]) != 0
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Resultsdir\" field. Provide a name for \
the results folder that will contain your analysis results."
		}

	post_types = config_dic["Post_types"]
	try:
		assert isinstance(post_types, list)
		assert len(post_types) != 0
		assert set(post_types) <= {"comments_and_reactions", "posts", "messages"}
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Post_types\" field. See the README file \
for more details on what to fill in this field."
		}

	analysis_period = config_dic["Analysis_period"]
	try:
		assert isinstance(analysis_period, list)
		assert len(analysis_period) != 0
		assert set(analysis_period) <= {"annual", "monthly", "global"}
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Analysis_period\" field. See the README \
file for more details on what to fill in this field."
		}

	return None


"""
	If the user specified usernames to check their interactions with, verify
	that the entries are in valid format.
"""


def name_check(config_dic):
	names = config_dic.get("Target_names", [])
	for name in names:
		try:
			assert isinstance(name, str)
		except AssertionError:
			return {
				"Invalid field": "Invalid name in \"Target_names\" field: {}. \
See the README file for more details on what to fill in this \
field.".format(str(name))
			}
	return None


"""
	Check if all fields relevant to post counting are present and are valid
	entries.
"""


def post_count_config_check(config_dic):
	try:
		assert "Count_config" in config_dic.keys()
	except AssertionError:
		return {"Missing field": "Missing \"Count_config\" field."}

	count_config = config_dic["Count_config"]
	count_config_req_keys = {
		"Char_limit_min",
		"Char_limit_max",
		"Word_limit_min",
		"Word_limit_max"
	}
	try:
		assert isinstance(count_config, dict)
		assert set(count_config.keys()) == count_config_req_keys
		for limit_int in count_config.values():
			assert isinstance(limit_int, int)
			assert limit_int >= 0
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Count_config\" field. See the README file \
for more details on what to fill in this field."
		}
	try:
		char_limit_min = count_config["Char_limit_min"]
		char_limit_max = count_config["Char_limit_max"]
		bothzero = (char_limit_min == 0 and char_limit_max == 0)
		min_lesser_than_max = char_limit_min < char_limit_max
		assert bothzero or min_lesser_than_max
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Count_config\" field. \
\"Char_limit_min\" must be lower than \"Char_limit_max\"."
		}
	try:
		word_limit_min = count_config["Word_limit_min"]
		word_limit_max = count_config["Word_limit_max"]
		bothzero = (word_limit_min == 0 and word_limit_max == 0)
		min_lesser_than_max = word_limit_min < word_limit_max
		assert bothzero or min_lesser_than_max
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Count_config\" field. \
\"Word_limit_min\" must be lower than \"Word_limit_max\"."
		}

	return None


"""
	Check if all fields relevant to the analyzer module are present and are
	valid entries.
"""


def analyzer_config_check(config_dic):
	try:
		assert "Analyzer_config" in config_dic.keys()
	except AssertionError:
		return {"Missing field": "Missing \"Analyzer_config\" field."}

	analyzer_config = config_dic["Analyzer_config"]
	analyzer_config_req_keys = {
		"SGrank_ngram",
		"SGrank_norm",
		"SGrank_top_count",
		"SGrank_top_ratio",
		"Textrank_norm",
		"Textrank_top_count",
		"Textrank_top_ratio"
	}
	config_str_keys = ["SGrank_norm", "Textrank_norm"]
	config_int_keys = ["SGrank_top_count", "Textrank_top_count"]
	config_float_keys = ["SGrank_top_ratio", "Textrank_top_ratio"]
	valid_norms = ['lemma', 'lower', '']
	try:
		assert isinstance(analyzer_config, dict)
		assert set(analyzer_config.keys()) == analyzer_config_req_keys
		assert isinstance(analyzer_config["SGrank_ngram"], list)
		for key in config_str_keys:
			assert isinstance(analyzer_config[key], str)
			assert analyzer_config[key] in valid_norms
		for key in config_int_keys:
			assert isinstance(analyzer_config[key], int)
			assert analyzer_config[key] >= 0
		for key in config_float_keys:
			assert isinstance(analyzer_config[key], float)
			assert analyzer_config[key] >= 0.0 and analyzer_config[key] <= 1.0
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Analyzer_config\" field. See the README file \
for more details on what to fill in this field."
		}

	sgrank_ngram = analyzer_config["SGrank_ngram"]
	try:
		assert len(sgrank_ngram) > 0
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Analyzer_config\" field. \
\"SGrank_ngram\" cannot be an empty list."
		}
	old_value = sgrank_ngram[0] - 1
	try:
		for value in sgrank_ngram:
			assert isinstance(value, int)
			assert value > 0
			assert value - old_value == 1
			old_value = value
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Analyzer_config\" field. \
\"SGrank_ngram\" must be a list of consecutive integers greater \
than 0."
		}

	sgrank_int = analyzer_config["SGrank_top_count"]
	sgrank_float = analyzer_config["SGrank_top_ratio"]
	try:
		assert not (sgrank_int == 0 and sgrank_float == 0.0)
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Analyzer_config\" field. \
\"SGrank_top_count\" and \"SGrank_top_ratio\" cannot both be set \
to 0."
		}

	textrank_int = analyzer_config["Textrank_top_count"]
	textrank_float = analyzer_config["Textrank_top_ratio"]
	try:
		assert not (textrank_int == 0 and textrank_float == 0.0)
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Analyzer_config\" field. \
\"Textrank_top_count\" and \"Textrank_top_ratio\" cannot both be \
set to 0."
		}

	return None


"""
	Check if all fields relevant to the smakstats module are present and are
	valid entries.
"""


def smakstats_config_check(config_dic):
	try:
		assert "SMAKstats_config" in config_dic.keys()
	except AssertionError:
		return {"Missing field": "Missing \"SMAKstats_config\" field."}

	smakstats_config = config_dic["SMAKstats_config"]
	smakstats_config_req_keys = {
		"Keyterm_limit",
		"Wordcount_limit"
	}
	try:
		assert isinstance(smakstats_config, dict)
		assert set(smakstats_config.keys()) == smakstats_config_req_keys
		for values in smakstats_config.values():
			assert isinstance(values, int)
			assert values > 0
	except AssertionError:
		return {
			"Invalid field": "Invalid \"SMAKstats_config\" field. See the README file \
for more details on what to fill in this field."
		}

	return None


"""
	Check if all fields relevant to results visualizer are present and are valid
	entries.
"""


def visualizer_config_check(config_dic):
	try:
		assert "Visualizer_config" in config_dic.keys()
	except AssertionError:
		return {"Missing field": "Missing \"Visualizer_config\" field."}

	visualizer_config = config_dic["Visualizer_config"]
	visualizer_config_req_keys = {
		"Wordcloud_width",
		"Wordcloud_height",
		"Wordcloud_limit",
		"URL_chart_upper_limit",
		"URL_chart_lower_limit",
		"Min_data_count",
		"Max_data_count"
	}
	try:
		assert isinstance(visualizer_config, dict)
		assert set(visualizer_config.keys()) == visualizer_config_req_keys
		for values in visualizer_config.values():
			assert isinstance(values, int)
			assert values > 0
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Visualizer_config\" field. See the README file \
for more details on what to fill in this field."
		}

	try:
		min_url_count = visualizer_config["URL_chart_lower_limit"]
		max_url_count = visualizer_config["URL_chart_upper_limit"]
		assert min_url_count < max_url_count
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Visualizer_config\" field. \
\"URL_chart_lower_limit\" must be lower than \
\"URL_chart_upper_limit\"."
		}

	try:
		min_data_count = visualizer_config["Min_data_count"]
		max_data_count = visualizer_config["Max_data_count"]
		assert min_data_count < max_data_count
	except AssertionError:
		return {
			"Invalid field": "Invalid values in \"Visualizer_config\" field. \
\"min_data_count\" must be lower than \"max_data_count\"."
		}

	return None


CONFIG_CHECK_FUNCTIONS = [
	basic_check,
	name_check,
	post_count_config_check,
	analyzer_config_check,
	smakstats_config_check,
	visualizer_config_check,
]


def parse_config(config_path):
	with open(config_path, "r") as f:
		config_dic = json.load(f)

	for func in CONFIG_CHECK_FUNCTIONS:
		err = func(config_dic)
		if err is not None:
			return None, err

	return config_dic, None
