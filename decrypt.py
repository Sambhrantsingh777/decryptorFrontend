# -*- coding: utf-8 -*-
from read_logs import get_logs_data
from Crypto.Cipher import AES
import os, array, random
from hashlib import pbkdf2_hmac
import json
import re
import shutil


def getEncryptionKey(appsflyer_key):
	key = pbkdf2_hmac(
		hash_name='sha1',
		password=bytes(appsflyer_key),
		salt=bytearray([0, 0, 0, 0, 0, 0, 0, 0]),
		iterations=10000,
		dklen=16
	)

	return [-256 + i if i > 127 else i for i in bytearray(key)]

def decrypt_data2(data,key,iv):
	data = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', data)
	key_new = array.array('b', key).tostring()
	iv_new = array.array('b', iv).tostring()
	cipher = AES.new(key_new, AES.MODE_CBC, iv_new )
	data = array.array('b', data).tostring()
	data = pad(data)
	decrypted_text = cipher.decrypt( data )
	# decrypted_text = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', decrypted_text)
	return decrypted_text

def decrypt_data(data,key,iv):
	dataArray = []
	for i in array.array('b', data):
		if (i < 0):
			dataArray.append(256 + i)
		else:
			dataArray.append(i)

	final_data = []
	for i in dataArray:
		if i > 127:
			final_data.append(-256 + i)
		else:
			final_data.append(i)

	iv = final_data[-24:-8]
	# print(final_data[-8:])

	data = array.array('b', final_data).tostring()

	key_new = array.array('b', key).tostring()
	iv_new = array.array('b', iv).tostring()
	cipher = AES.new(key_new, AES.MODE_CBC, iv_new)
	
	data = pad(data)
	decrypted_text = cipher.decrypt( data )
	decrypted_text = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', decrypted_text)
	return decrypted_text

def pad(s):
	bs = AES.block_size
	return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

def unpad(s):
	return s[:-ord(s[len(s) - 1:])]

def getIV():
	iv = []
	for _ in range(16):
		iv += [random.randint(-120, 120)]
	return iv

def start(folder, filename, KEY):
	try:
		os.mkdir('{}'.format(folder))
		os.mkdir('{}/{}'.format(folder, 'Input/'))
		os.mkdir('{}/{}'.format(folder,'Input/res/'))
	except:
		shutil.rmtree(folder)
		os.mkdir('{}'.format(folder))
		os.mkdir('{}/{}'.format(folder, 'Input/'))
		os.mkdir('{}/{}'.format(folder, 'Input/res/'))

	path = os.getcwd()
	logs_data = get_logs_data('{}/{}'.format(path, filename), "/"+folder).get('logs')

	size = len(logs_data.get('seq'))
	output = ''
	for i in range(size):
		if 'appsflyer' in logs_data.get('urls')[i]:
			if 1:
				# if logs_data.get('urls')[i] == 'https://launches.appsflyer.com/api/v5.4/androidevent':
				output += "<br>####################################################################<br>"
				output += logs_data.get('urls')[i]+"<br>"
				# print(logs_data.get('data')[i])
				output += "<br>%%%%%%%%%%%%%%%%^^^^^^^^^^^^%%%%%%%%%%%%%%%<br>"
				if str(logs_data.get('data')[i])[:1] == '{' and str(logs_data.get('data')[i])[-1:] == '}':
					data = logs_data.get('data')[i]
				else:
					try:
						data = decrypt_data(logs_data.get('data')[i], getEncryptionKey(KEY), getIV())
						if '"}' in data:
							data = data.rsplit('"}',1)[0]+'"}'
						data = json.loads(data)
					except Exception as e3:
						try:
							output += "1:::"+str(e3)+"<br>"
							data = decrypt_data2(logs_data.get('data')[i], getEncryptionKey(KEY), getIV())
							# data = appsflyer.CRYPTO.decrypt_data(logs_data.get('data')[i], KEY)
						except Exception as e2:
							output += logs_data.get('data')[i]+"<br>"
							output += "2:::"+str(e2)+"<br>"
							data = {}
				try:
					output += json.dumps(data, sort_keys=True)+"<br>"
				except:
					output += data+"<br>"

				output += "<br>####################################################################<br><br>"
				print('')
				print('')
			# except Exception as e:
			# 	print(e)
			# 	print('')
			# 	print("COULD NOT DECODE")
			# 	print('')

	shutil.rmtree(folder)
	os.remove(filename)

	return output