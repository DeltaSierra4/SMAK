from collections import defaultdict
from itertools import chain
import os
import os.path as op
import json
import strprocutil

"""
	JSON loader module for the Social media analytics tool.
	Loads JSON files containing relevant data in the provided directory.

	@author: DeltaSierra4
"""

"""
	load_json() from directory that contains json files with your comments
	and posts. This is a wrapper method to load individual json files by their
	specific categories: "comments", "messages", and "posts"
"""


def load_json(data_dir, subdir, username):
	component_dir = op.join(data_dir, subdir)
	if subdir == "comments":
		component_dir = op.join(component_dir, "comments.json")
		return load_comment_json(component_dir, username)
	elif subdir == "posts":
		return load_post_json(
			os.listdir(component_dir),
			component_dir, username
		)
	else:
		# Lots of useless subdirectories here. We are only interested in the
		# inbox subdirectory.
		component_dir = op.join(component_dir, "inbox")
		return load_message_json(
			os.listdir(component_dir),
			component_dir, username
		)


"""
	load_comment_json() from sub directory that contains comments.
	Return dictionary is split into a dictionary of comments outside of groups
	and a dictionary of comments within a group. Each dictionary is further
	separated into comments on my own post, comments on another person's or
	page's post, and any replies. The comments for other people and replies
	are further separated by names of people that the user is interacting with.
"""


def load_comment_json(comment_dir, username):
	comment_dic = {
		"NonGroup": {
			"Own": [],
			"Other": defaultdict(lambda: []),
			"Replies": defaultdict(lambda: []),
		},
		"Group": {
			"Own": [],
			"Other": defaultdict(lambda: []),
			"Replies": defaultdict(lambda: []),
		},
	}
	with open(comment_dir, 'r') as f:
		data = json.load(f)["comments"]
		for data_row in data:
			if invalid_comment(data_row):
				continue
			ts = data_row["timestamp"]
			comment_list = data_row["data"]
			title = strprocutil.convert_str(data_row["title"])[:-1]

			# To ensure that all title data is processed correctly, we only
			# process comments that are obviously made by the user.
			# This is why the user must put in their correct username.
			if username not in title:
				continue

			for comment in comment_list:
				comment_data = comment.get("comment", {})
				comment_text = comment_data.get("comment", "")
				if len(comment_text) == 0:
					continue
				c_type, o_name, c_dic = load_comment_row(
					ts, comment_text, title, username
				)
				if c_type == "":
					continue
				comment_group = comment_data.get("group", "")
				if comment_group:
					c_dic["Group name"] = comment_group
					if o_name:
						comment_dic["Group"][c_type][o_name].append(c_dic)
					else:
						comment_dic["Group"][c_type].append(c_dic)
				else:
					if o_name:
						comment_dic["NonGroup"][c_type][o_name].append(c_dic)
					else:
						comment_dic["NonGroup"][c_type].append(c_dic)
	return comment_dic


"""
	load_post_json() from sub directory that contains posts.

	Takes in a list of all json files in the posts directory and selectively
	parses through json files that contain posts only (i.e. Ignores json files
	containing notes).

	Return dictionary is split into comment on my own post, post on another
	person's wall, and posts on a group or page. Uncategorized posts go into
	a "Misc_post" category.
"""


def load_post_json(post_dir_list, post_dir, username):
	valid_json = []
	for filename in post_dir_list:
		if "your_posts" in filename:
			valid_json.append(filename)

	post_dic = defaultdict(lambda: [])
	for filename in valid_json:
		json_file = op.join(post_dir, filename)
		with open(json_file, 'r') as f:
			datarows = json.load(f)
			for item in datarows:
				if invalid_row(item):
					continue
				if "title" not in item:
					# Occasionally, posts without titles indicating where they
					# were posted come up. We classify them as miscellaneous
					# posts.
					post_dic["Misc_post"] = list(
						chain(post_dic["Misc_post"], load_post_row(item))
					)
				else:
					# If title data is found, use it to extract whose wall was
					# the post made on. Clip off the last period from the title
					# before using it.
					title = strprocutil.convert_str(item["title"])[:-1]

					# To ensure that all title data is processed correctly, we only
					# process comments that are obviously made by the user.
					# This is why the user must put in their correct username.
					if username not in title:
						continue

					if title[-8:] == "timeline":
						# Post was made on a friend's wall
						name = name_extractor(title, "fr", username)
						if name == "":
							continue
						post_dic[name] = list(chain(post_dic[name], load_post_row(item)))
					elif own_post(title, username):
						# Post was made on your own wall
						post_dic[username] = list(chain(post_dic[username], load_post_row(item)))
					elif group_page_event_post(title, username):
						# Post was made on a group, page, or event
						name = name_extractor(title, "gr", username)
						if name == "":
							continue
						post_dic[name] = list(chain(post_dic[name], load_post_row(item)))
					else:
						# Treat these as miscellaneous posts
						post_dic["Misc_post"] = list(
							chain(post_dic["Misc_post"], load_post_row(item))
						)
	return post_dic


"""
	load_message_json() from sub directory that contains posts.

	Takes in a list of all json files in the posts directory and selectively
	parses through json files that contain posts only (i.e. Ignores photos,
	gifs, or videos).

	Return dictionary is split into single DM or group DM, further split
	by individual associated with the messaging.
"""


def load_message_json(mess_dir_list, mess_dir, username):
	valid_json = []
	for filename in mess_dir_list:
		individual_dir = op.join(mess_dir, filename)
		for file in os.listdir(individual_dir):
			if "message" in file and op.splitext(file)[1] == ".json":
				valid_json.append(op.join(individual_dir, file))

	mess_dic = {
		"NonGroup": defaultdict(lambda: []),
		"Group": defaultdict(lambda: []),
	}
	for filename in valid_json:
		with open(filename, 'r') as f:
			data = json.load(f)
			if invalid_message_json(data):
				continue
			participants = data["participants"]
			messages = data["messages"]
			name = strprocutil.convert_str(data["title"])
			messlist = load_message_row(messages, username)
			if len(messlist) == 0:
				continue
			if len(participants) <= 2:
				# Individual message to either oneself or a friend.
				mess_dic["NonGroup"][name] = messlist
			else:
				# Group message
				mess_dic["Group"][name] = messlist
	return mess_dic


"""
	Checks if a comment contains all relevant information (i.e. timestamp,
	content, and title). Returns True if either is missing.
"""


def invalid_comment(data_row):
	ts = data_row.get("timestamp", -1)
	title = data_row.get("title", "").strip()
	data_list = data_row.get("data", [])
	# A creative way to check if all of them are present and make sure that
	# they are not degenerate data such as empty strings.
	return (ts * len(title) * len(data_list) <= 0)


"""
	Checks if a data_row contains all relevant information (i.e. timestamp and
	content). Returns True if either is missing.

	Note: A post can either contain a "post" if it is a post on a timeline, or
	it can be a "description" of a "media" if it's a photo/video post. The
	load_post_row() will prioritize finding "post" instances, but if none are
	found, it'll look for "description" instances. The invalid_row() check
	only checks if either are present.
"""


def invalid_row(data_row):
	ts = data_row.get("timestamp", -1)
	if ts <= 0:
		return True
	data_list = data_row.get("data", [])
	post_found = False
	for data in data_list:
		if "post" in data and len(data.get("post", "").strip()) > 0:
			post_found = True
			break
	if not post_found:
		attachment_list = data_row.get("attachments", [])
		for data_dic in attachment_list:
			data_list = data_dic.get("data", [])
			for data in data_list:
				if "media" in data and len(data.get("description", "").strip()) > 0:
					media_data = data["media"]
					if "description" in media_data:
						post_found = True
						break
	return not post_found


"""
	Checks if a message.json contains all relevant information (i.e.
	participants, messages, title, and thread_type). Returns True if any are
	missing.
"""


def invalid_message_json(data_row):
	participants = data_row.get("participants", [])
	messages = data_row.get("messages", [])
	title = data_row.get("title", "").strip()
	t_type = data_row.get("thread_type", "").strip()
	# A creative way to check if all of them are present and make sure that
	# they are not degenerate data such as empty strings.
	return (len(participants) * len(messages) * len(title) * len(t_type) == 0)


"""
	load_comment_row() with necessary information and returns two strings and
	a dictionary.

	The first string indicates whether this is a comment on user's own post, a
	comment on someone else's post, or a reply to someone. The second string
	is the name of the person the user is interacting with, in case it is a
	comment to another person's post or a reply. The dictionary contains the
	timestamp and the message itself.

	Returns an empty string if an illegitimate data row is encountered.
"""


def load_comment_row(ts, comment, title, username):
	c_dic = {
		"ts": ts,
		"post": strprocutil.convert_str(comment),
	}
	# Next step is to extract information out of the title. Default case is
	# assuming it as a comment to another person's post.
	comment_nature = "Other"
	comment_target = ""
	title_words = title.split()
	name_w = len(username.split())
	if "replied" in title_words:
		comment_nature = "Replies"
	elif title_words[name_w] == "commented" and title_words[name_w + 3] == "own":
		comment_nature = "Own"
	if comment_nature != "Own":
		comment_target = name_extractor(title, "co", username)
		if len(comment_target) == 0:
			return "", "", {}
	return comment_nature, comment_target, c_dic


"""
	load_post_row() from json file that contains posts.

	Takes in the raw data row taken from a json file and preprocesses it to
	utf-encoded strings, then returns a list of dictionaries containing the
	timestamp and content of the post.

	Note: A post can either contain a "post" if it is a post on a timeline, or
	it can be a "description" of a "media" if it's a photo/video post. The
	load_post_row() will prioritize finding "post" instances, but if none are
	found, it'll look for "description" instances. The invalid_row() check
	ensures that all data_row are valid entries containing either.
"""


def load_post_row(data_row):
	posts = []
	data_list = data_row.get("data", [])
	for data in data_list:
		if "post" in data:
			posts.append({
				"ts": data_row["timestamp"],
				"post": strprocutil.convert_str(data["post"]),
				"type": "Regular",
			})
	# Here we look for photo posts, but we'll only add photo posts that are
	# not duplicates of the original post.
	attachment_list = data_row.get("attachments", [])
	for data_dic in attachment_list:
		data_list = data_dic.get("data", [])
		for data in data_list:
			if "media" in data:
				media_data = data["media"]
				if "description" in media_data:
					photo_post = strprocutil.convert_str(media_data["description"])
					if photo_post not in [item["post"] for item in posts]:
						posts.append({
							"ts": media_data.get("creation_timestamp", data_row["timestamp"]),
							"post": photo_post,
							"type": "Photo",
						})
	return posts


"""
	load_message_row() from json file that contains messages.

	Takes in the raw data row taken from a json file and preprocesses it to
	utf-encoded strings, then returns a list containing the timestamp and
	content of the post.

	NB! message.json files store timestamp in units of milliseconds. This
	must be corrected to units of seconds, or timestamp conversion will fail.
"""


def load_message_row(message_list, username):
	my_messages = []
	for data in message_list:
		sender = strprocutil.convert_str(data.get("sender_name", "")).strip()
		message = strprocutil.convert_str(data.get("content", "")).strip()
		mtype = data.get("type", "").strip()
		ts = int(data.get("timestamp_ms", -1) / 1000)  # conversion to seconds
		# A creative way to check if all of them are present and make sure that
		# they are not degenerate data such as empty strings.
		if len(sender) * len(message) * len(mtype) * ts <= 0:
			continue
		# Only looking for actual messages, not logs of adding/removing people
		# in group chats. Also check if they're from username only.
		if (mtype != "Generic" and mtype != "Share") or sender != username:
			continue
		# Last but not least, ignore any messages that say something like
		# "You set your nickname to xxx."
		if len(message) >= 24 and message[:24] == "You set your nickname to":
			continue
		my_messages.append({
			"ts": ts,
			"post": message,
		})
	return my_messages


"""
	Helper method that checks if a post was made on one's own wall.
"""


def own_post(title, username):
	title_words = title.split()
	namewc = len(username.split())
	# Ignore all group/event page posts
	if not ("group:" in title_words or "event:" in title_words):
		# First format: John Doe updated his status
		if title_words[-1] == "status" and title_words[-3] == "updated":
			return True
		# Second format: John Doe is feeling emotion
		if title_words[namewc] == "is" and title_words[namewc + 1] == "feeling":
				return True
		if title_words[-2] == "feeling" and title_words[-3] == "is":
			return True
		# Third format: John Doe shared a memory
		if title_words[-1] == "memory" and title_words[-2] == "a":
			return True
		# Fourth format: John Doe uploaded a new photo/video(s)
		if title_words[-2] == "new":
			if "photo" in title_words[-1] or "video" in title_words[-1]:
				return True
		# Fifth format: John Doe answered a question
		if title_words[-1] == "question" and title_words[-3] == "answered":
			return True
		# Sixth format: John Doe was with Mary Jane [and x others] [at y] [in z]
		# A similar format can be the following:
		# John Doe was celebrating friendship with Mary Jane
		# John Doe was looking for recommendations
		# John Doe was attending Storm Area 69
		# John Doe was live
		if title_words[namewc] == "was":
			tag_another = ["with", "at", "in", "live"]
			activities = ["celebrating", "looking", "attending", "eating"]
			if title_words[namewc + 1] in tag_another + activities:
				return True
		# Seventh format: Sharing other media
		# John Doe shared a video from the playlist My Playlist
		# John Doe shared an episode of Some Scary Movie
		# John Doe shared a quote
		# John Doe shared moments from his year
		if title_words[namewc] == "shared":
			shared_media = ["video", "quote", "episode"]
			if title_words[namewc + 2] in shared_media:
				return True
			elif title_words[namewc + 1] == "moments":
				return True
		# Eighth format: John Doe created a poll
		if title_words[-1] == "poll" and title_words[-3] == "created":
			return True
		# Ninth format: John Doe was 🎉 celebrating friendship
		if title_words[-1] == "friendship" and title_words[-2] == "celebrating":
			return True
	return False


"""
	Helper method that checks if a post was made in a group, page, or an event.

	TODO! Handle these titles:
	John Doe contributed to the album: <album name> in <group name>
"""


def group_page_event_post(title, username):
	title_words = title.split()
	namewc = len(username.split())
	# First format: John Doe posted in group/event/page
	if title_words[namewc] == "posted" and title_words[namewc + 1] == "in":
		return True
	# Second format: John Doe shared a link to the group/event/page: name
	# Related: John Doe shared an album: <Album name> to the group: name
	# Any title containing both "shared an xxx" and "to the group/event/page"
	# can count as this.
	grp_evt_pg = ["to the group:", "to the event:"]
	rep_title = title.replace(username, "").strip()
	if rep_title[:8] == "shared a":
		for ke in grp_evt_pg:
			if ke in rep_title:
				return True
	if title_words[namewc] == "shared" and title_words[namewc + 5] in grp_evt_pg:
		# Check for a degenerate case
		if title_words[namewc + 2] != "album:":
			return True
	# Third format: John Doe created a [private] event for group name
	if title_words[namewc] == "created":
		event_keyword = ["event", "private"]
		if title_words[namewc + 2] in event_keyword:
			return True

	"""
	grp_evt_pg_post = ["posted in", "to the group", "to the event"]
	for exp in grp_evt_pg_post:
		# First, take care of the degenerate case of someone attempting to
		# use a name that matches one of the key expressions.
		if title.find(exp) == 0:
			title = title.replace(exp, "your name", 1)
		if exp in title:
			return True
	"""
	return False


"""
	Helper method that extracts friend's name or group's name, depending on the
	friend_name parameter. It also checks if the title is related to a post or
	a comment.
"""


def name_extractor(title, friend_name, username):
	# First two cases involve posts on another user's timeline.
	if friend_name == "fr":
		# Titles are in the following format:
		# Username wrote on John Doe's timeline
		# Username added a new photo/video to John Doe's timeline
		# Username shared a memory to John Doe's timeline
		key_exp = ["wrote on", "memory to", "photo to", "video to"]
	elif friend_name == "gr":
		# Format of title will be either one of the following:
		# John Doe posted in Group Name
		# John Doe shared a post to the group: Group Name
		key_exp = ["posted in", "the group:", "the event:"]
	else:
		# This case involves a comment with another user.
		key_exp = ["commented on", "replied to"]

	# First, take care of the degenerate case of someone attempting to
	# use a name that matches one of the key expressions.
	title = keyexp_username_prune(title, key_exp, username)

	if friend_name == "fr":
		return_name = " ".join(title.split()[2:-1])[:-2]
	elif friend_name == "gr":
		return_name = " ".join(title.split()[2:])
	else:
		# At this point, all comments are in one of the four following formats.
		# "commented on John Doe's post"
		# "commented on John Doe's live video"
		# "replied to John Doe's comment"
		# "replied to one's own comment"
		target_name_list = title.split()[2:-1]
		if target_name_list[-1] == "live" or target_name_list[-1] == "life":
			target_name_list = target_name_list[:-1]
		if target_name_list[-1] == "own":
			return_name = username
		else:
			return_name = " ".join(target_name_list)[:-2]
	return return_name


"""
	Helper method that takes care of degenerate cases from title data where
	someone attempts to use a user name or page name that matches one of the
	key expressions we are looking for.

	e.g. key expression of "commented on", and a Facebook page with the name of
	"I replied to yo mommas phonecall", dealing with the following title:
	I replied to yo mommas phonecall replied to John Doe's comment.

	The first find() results will match to the username, so we replace those
	instances until there are no occurrences left before the actual key
	phrase.
"""


def keyexp_username_prune(title, keyexp, username):
	for exp in keyexp:
		while exp in username:
			title = title.replace(exp, "your name", 1)
			username = username.replace(exp, "your name", 1)
	key_exp_loc = [title.find(ke) for ke in keyexp]
	if sum(key_exp_loc) == -(len(keyexp)):
		# All titles at this point must have either one of the above key_exp.
		# If it contains neither, consider it an illegitimate data row and
		# return an empty string.
		title = ""
	elif key_exp_loc.count(-1) == len(keyexp) - 1:
		# Only one key expression found. Most titles should fall into this
		# category.
		title = title[max(key_exp_loc):]
	else:
		# Multiple key expressions found. This is the case in the edge case
		# scenario where the target's name contains key expressions.
		# In this case, we want to look at the lowest index of the two
		# find() results.
		title = title[min(key_exp_loc):]
	return title
