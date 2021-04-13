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


"""
	Check if all basic fields are present and are valid entries.
"""


def basic_check(config_dic):
	config_keys = config_dic.keys()
	basic_fields = ["Language", "Username", "Datadir", "Post_types"]
	for field in basic_fields:
		try:
			assert field in config_keys
		except AssertionError:
			return {"Missing field": "Missing \"{}\" field.".format(field)}

	data_dir = config_dic["Datadir"]
	try:
		assert op.exists(data_dir)
	except AssertionError:
		return {"FNF": "{} is not a valid path.".format(data_dir)}

	post_types = config_dic["Post_types"]
	try:
		assert isinstance(post_types, list)
		assert len(post_types) != 0
		assert set(post_types) <= {"comments", "posts", "messages"}
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Post_types\" field. See the README file \
			for more details on what to fill in this field."
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
	count_config_req_keys = [
		"Char_limit_min",
		"Char_limit_max",
		"Word_limit_min",
		"Word_limit_max"
	]
	try:
		assert isinstance(count_config, dict)
		assert list(count_config.keys()) == count_config_req_keys
		for limit_int in count_config.values():
			assert isinstance(limit_int, int)
	except AssertionError:
		return {
			"Invalid field": "Invalid \"Count_config\" field. See the README file \
			for more details on what to fill in this field."
		}

	return None


CONFIG_CHECK_FUNCTIONS = [
	basic_check,
	post_count_config_check,
]
# TODO! Add a section for post_stats_config in the config.json to address the analysis portion (e.g. sgrank tuples, post length limits)


def parse_config(config_path):
	with open(config_path, "r") as f:
		config_dic = json.load(f)

	for func in CONFIG_CHECK_FUNCTIONS:
		err = func(config_dic)
		if err is not None:
			return None, err

	return config_dic, None
