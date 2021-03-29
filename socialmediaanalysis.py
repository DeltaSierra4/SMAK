import jsonloader
import postanalyzer
import smakstats
import tsconverter

import json
import os.path as op
import plac

"""
	Social media analytics tool written in Python with Textacy.

	flake8 --ignore=W191,E117 ./*.py << use this to check scripts

	@author DeltaSierra4
"""


SUB_DIRECTORIES = ["comments", "messages", "posts"]


@plac.annotations(
	data_dir=("Directory of JSON files", "positional", None, str),
	username=("Your Facebook username", "positional", None, str),
)
def main(data_dir, username):
	if not op.exists(data_dir):
		raise ValueError("Provide the directory that contains all data.")

	master_dic = {}
	for subdir in SUB_DIRECTORIES:
		master_dic[subdir] = jsonloader.load_json(data_dir, subdir, username)

	tsconverter.ts_dt_conv(master_dic, SUB_DIRECTORIES)

	tsconverter.sort_by_date(master_dic, SUB_DIRECTORIES)

	post_count_dic = postanalyzer.post_counts(
		master_dic, username, SUB_DIRECTORIES
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

	pruned_result_dic = smakstats.parse_results(result_dic, SUB_DIRECTORIES)

	# Save parse results as JSON file.
	with open("./parse_results.json", 'w+') as f2:
		json.dump(pruned_result_dic, f2, indent=4, sort_keys=True)

	pruned_count_dic = smakstats.parse_counts(post_count_dic, SUB_DIRECTORIES)

	# Save count results as JSON file.
	with open("./count_results.json", 'w+') as f2:
		json.dump(pruned_count_dic, f2, indent=4, sort_keys=True)


if __name__ == "__main__":
	plac.call(main)
