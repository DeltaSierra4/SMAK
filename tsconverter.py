from collections import defaultdict
from datetime import datetime

"""
	Timestamp converter module for the Social Media Analytics Kit.
	Performs various timestamp conversions into dates (year-month-day format)
	as well as date-related operations.

	@author: DeltaSierra4
"""


"""
	Wrapper method for converting timestamps to dates.
"""


def ts_dt_conv(master_dic, subdir):
	for sub in subdir:
		iter_conv(master_dic[sub])


"""
	Wrapper method to sort_by_date() all posts in each categories.
"""


def sort_by_date(master_dic, subdir):
	for sub in subdir:
		iter_sort(master_dic[sub])


"""
	Helper method that recursively iterates through dictionaries and converts
	all timestamp entries in the dictionary into year-month-date-hour formats.

	Data upon entrance:
	{
		"ts": 1600000000,
		"post": "This is a post",
		["type": "Regular"], # Only included if is_post == True
	}

	Data upon return:
	{
		"year": 2020,
		"month": 9,
		"day": 13,
		"hour": 5,
		["type": "Regular"], # Only included if is_post == True
	}

	is_post is set to True if we're dealing with a normal post (i.e. not a
	comment or a message).
"""


def iter_conv(dic):
	for key, value in dic.items():
		if isinstance(value, dict):
			iter_conv(value)
		else:
			dic[key] = [
				{
					"ts": p["ts"],
					"year": int(datetime.fromtimestamp(p["ts"]).year),
					"month": int(datetime.fromtimestamp(p["ts"]).month),
					"day": int(datetime.fromtimestamp(p["ts"]).day),
					"hour": int(datetime.fromtimestamp(p["ts"]).hour),
					"post": p["post"],
					"type": p.get("type", ""),
				} for p in value
			]


"""
	Helper method that recursively iterates through dictionaries and sorts
	all entries in a list into dictionary formats based on their year, month,
	day, and hour.

	Data upon entrance:
	"Username": [
		{
			"year": 2020,
			"month": 9,
			"day": 13,
			"hour": 5,
			"post": "This is a post",
			["type": "Regular"], # Only included if is_post == True
		}
	]

	Data upon return:
	"Username": {
		2020: {
			9: {
				13: {
					"day": [
						{
							"post": "This is a post",
							["type": "Regular"], # Only included if is_post == True
						}
					],
				},
			},
		},
	}

	is_post is set to True if we're dealing with a normal post (i.e. not a
	comment or a message).
"""


def iter_sort(dic):
	for key, value in dic.items():
		if isinstance(value, dict):
			iter_sort(value)
		else:
			sorted_dic = defaultdict(
				lambda: defaultdict(
					lambda: defaultdict(
						lambda: defaultdict(lambda: [])
					)
				)
			)
			for post in value:
				p_y = post["year"]
				p_m = post["month"]
				p_d = post["day"]
				if post["hour"] < 18 and post["hour"] >= 6:
					p_dt = "day"
				else:
					p_dt = "night"
				post_dic = {
					"post": post["post"],
					"type": post.get("type", ""),
				}
				sorted_dic[p_y][p_m][p_d][p_dt].append(post_dic)
			dic[key] = sorted_dic
