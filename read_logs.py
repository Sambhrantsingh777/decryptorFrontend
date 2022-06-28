# -*- coding: utf-8 -*-
import os, sys, urlparse
import subprocess
import shutil
import zipfile
import json

beautifulSoup_import_error = None


class start_processing:
	def __init__(self, index_file_str, raw=None):
		"""* 
			>>>>SET INDEX FILE DATA AND PATH FOR RAW DATA EXTRACTED FROM LOGS<<<<
		*"""
		self.index_file = index_file_str
		self.raw_path = raw


	"""* 
		>>>>FUNCTION TO PROCESS DATA IN LOGS AND EXTRACT DATA SET FROM THE SAME<<<<
	*"""
	def process_raw_data(self):
		count = 0
		seq = []
		url_list = []
		query_param_list = []
		data_list = []
		headers_list = []
		methods_list = []
		folder = os.listdir(self.raw_path)
		file_list = sorted(folder)
		"""* 
			>>>>ITERATING THROUGH ALL THE FILES IN EXTRACTED LOGS RAW FOLDER<<<<
		*"""
		for file in file_list:
			if file.endswith('_c.txt'):
				count += 1
				raw_file = open(self.raw_path + file)
				str_of_raw_file = ''
				for line in raw_file.readlines():
					str_of_raw_file += line
				raw_file.close()
				with open(self.raw_path + file.replace('c', 's')) as f2:
					response_file = f2.readline()
				f2.close()
				if not ":443" in str_of_raw_file:
					if "200" in response_file or "500" in response_file:
						HEAD = str_of_raw_file.split('\n\r')[0]
						############## DATA FORMATTING ############
						if "POST " in HEAD or "GET " in HEAD or "HEAD " in HEAD or "PUT " in HEAD:
							try:
								DATA = str_of_raw_file.split('\n\n')[1]
							except Exception as e:
								DATA = str_of_raw_file.replace(HEAD,'').strip()
							if "{" in DATA:
								try:
									data = json.loads(DATA.strip('\n'))
								except:
									try:
										data = eval(DATA.strip('\n'))
									except:
										try:
											data = DATA
										except:
											data = "UNREADABLE DICTIONARY"

								data_list.append(data)
							else:
								try:
									data_list.append(dict(urlparse.parse_qsl(DATA, keep_blank_values=True)))
								except:
									data_list.append("Unrecognized Data")

						########## URL & QUERY DATA EXTRACTION ###########
						if "POST " in HEAD:
							methods_list.append("post")
							url = HEAD.split("POST ")[1].split(" ")[0]
							if '?' in url:
								query_param_list.append(dict(urlparse.parse_qsl(url.split('?')[1], keep_blank_values=True)))
								url_list.append(url.split('?')[0])
							else:
								url_list.append(url)
								query_param_list.append(None)

						elif "GET " in HEAD:
							methods_list.append("get")
							url = HEAD.split("GET ")[1].split(" ")[0]
							if '?' in url:
								query_param_list.append(dict(urlparse.parse_qsl(url.split('?')[1], keep_blank_values=True)))
								url_list.append(url.split('?')[0])
							else:
								url_list.append(url)
								query_param_list.append(None)

						elif "HEAD " in HEAD:
							methods_list.append("head")
							url = HEAD.split("HEAD ")[1].split(" ")[0]
							if '?' in url:
								query_param_list.append(dict(urlparse.parse_qsl(url.split('?')[1], keep_blank_values=True)))
								url_list.append(url.split('?')[0])
							else:
								url_list.append(url)
								query_param_list.append(None)

						elif "PUT " in HEAD:
							methods_list.append("put")
							url = HEAD.split("PUT ")[1].split(" ")[0]
							if '?' in url:
								query_param_list.append(dict(urlparse.parse_qsl(url.split('?')[1], keep_blank_values=True)))
								url_list.append(url.split('?')[0])
							else:
								url_list.append(url)
								query_param_list.append(None)

						###########HEADER DATA FORMATTING ##########
						if "POST " in HEAD or "GET " in HEAD or "HEAD " in HEAD or "PUT " in HEAD:
							if len(HEAD.split('HTTP/1.1\n')) > 1:
								try:
									headers_list.append(eval(("{'" + HEAD.split('HTTP/1.1\n')[1].split('\n\n')[
										0].replace('\n', "','").replace(": ", "':'") + "'}")))
								except:
									headers_list.append({})
							elif len(HEAD.split('HTTP/1.1')) > 1:
								dt="{"
								for kv in HEAD.strip().split('\n'):
									if 'HTTP/1.1' in kv:
										continue
									dt+="'"+kv.strip('\r').replace(': ',"': '")+"', "
								dt = dt+"}".replace(', }','}')
								try:
									headers_list.append(eval(dt))
								except:
									headers_list.append({})
							else:
								headers_list.append({})
							seq.append(count)

		return url_list, headers_list, query_param_list, data_list, methods_list, seq


def get_logs_data(logs, sub_path):
	queue = {}
	# 1)####################### .SAZ EXTRACTION ##########################
	getPath = os.getcwd()
	shutil.copy2(logs, getPath + "/{}/Input/res/source.zip".format(sub_path))
	with zipfile.ZipFile(getPath + "/{}/Input/res/source.zip".format(sub_path), 'r') as zip_ref:
		zip_ref.extractall(getPath + '/{}/Input/res/extracted'.format(sub_path))

	# 2)################## LOCATE TO RAW DATA RESOURCE ####################
	raw = getPath + '{}/Input/res/extracted/raw/'.format(sub_path)
	formatted_data = start_processing(None, raw).process_raw_data()
	hostsList = []
	for d in formatted_data[0]:
		hostsList.append(d.split('//')[1].split('/')[0])

	# 3)####################### FINAL DATA DICT ###########################

	# return {'seq': formatted_data[5], 'hosts': hostsList, 'urls': formatted_data[0], 'headers': formatted_data[1],
	# 		'params': formatted_data[2], 'data': formatted_data[3], 'methods': formatted_data[4]}
	queue['logs'] = {'seq': formatted_data[5], 'hosts': hostsList, 'urls': formatted_data[0], 'headers': formatted_data[1],
			'params': formatted_data[2], 'data': formatted_data[3], 'methods': formatted_data[4]}

	return queue

######getPath + '/Input/'+log_file_name