import config_load
import jsonloader
import postanalyzer
import resultvisualizer
import smakstats
import strprocutil
import tsconverter

import json
import os.path as op
import plac

"""
	Social media analytics tool written in Python with Textacy.

	flake8 --ignore=W191,E117 ./*.py << use this to check scripts

	@author DeltaSierra4
"""


@plac.annotations(
	config_path=("Path to config file", "positional", None, str),
)
def main(config_path):
	if not op.exists(config_path):
		raise ValueError("Provide the directory that contains the config file.")

	config, err = config_load.parse_config(config_path)
	if err is not None:
		config_load.print_error(err)
		return
	data_dir = config["Datadir"]
	username = strprocutil.convert_unicode(config["Username"])
	sub_directories = config["Post_types"]

	master_dic = {}
	for subdir in sub_directories:
		master_dic[subdir] = jsonloader.load_json(data_dir, subdir, username)

	tsconverter.ts_dt_conv(master_dic, sub_directories)

	tsconverter.sort_by_date(master_dic, sub_directories)

	count_config = config["Count_config"]
	post_count_dic = postanalyzer.post_counts(
		master_dic, username, sub_directories, count_config
	)

	"""
		Now we have a dictionary of all posts divided into comments, posts, and
		messages, all with associated dates and hours.
		Analytics will be performed on multiple different levels: Each category,
		each individual involved, and each month.
		To be implemented: Analytics based on specific days of month, time of the
		day, and so on.
		The level of analytics gradually increases in level: Monthly -> yearly ->
		All time / Low category -> mid category -> high category (e.g. individual
		-> group -> global)
		Order of priority within dictionary: category > individual > time
		Results will be presented in a format that reflects the original
		dictionary.
	"""

	result_dic = postanalyzer.analyze(master_dic, username)

	pruned_result_dic = smakstats.parse_results(result_dic, sub_directories)

	# Save parse results as JSON file.
	with open("./parse_results.json", 'w+') as f2:
		json.dump(pruned_result_dic, f2, indent=4, sort_keys=True)

	pruned_count_dic = smakstats.parse_counts(post_count_dic, sub_directories)

	# Save count results as JSON file.
	with open("./count_results.json", 'w+') as f2:
		json.dump(pruned_count_dic, f2, indent=4, sort_keys=True)

	resultvisualizer.wordcloud_gen(pruned_result_dic)
	resultvisualizer.url_chart_gen(pruned_result_dic)
	resultvisualizer.stat_chart_gen(pruned_result_dic)


if __name__ == "__main__":
	plac.call(main)
