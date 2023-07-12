""" Helper functions """
try:
	import os, configparser, time, random
	from loguru import logger as log
	from sys import platform

except:
	raise

def clear():
	if platform=='win32':
		return os.system('cls')
	else:
		return os.system('clear')

######################## CONFIG AND GLOBALS #########################

MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = MINUTE_IN_SECONDS*60
DAY_IN_SECONDS = HOUR_IN_SECONDS*24
WEEK_IN_SECONDS = DAY_IN_SECONDS*7
MONTH_IN_SECONDS = DAY_IN_SECONDS*30

NOWAIT = False

def load_config(file="config.ini", delimiters=("=")):
	
	from pathlib import Path

	config = None

	if os.path.isfile(file):
		config = configparser.ConfigParser(allow_no_value=True, delimiters=delimiters)
		try:
			config.read(file)
		except:
			exit("ERROR loading configuration file.")

	return config

@log.catch()
def printTitle(title):
	clear()
	print("\n")
	print("= "*20)
	print(" "+str(title))
	print("= "*20)
	print("\n")

@log.catch()
def printHeading(title):
	print("\n")
	print("- "*20)
	print(" "+str(title))
	print("- "*20)
	print("\n")

@log.catch()
async def async_wait(t=0):
	import asyncio
	if not t:
		t = random.randrange(10,30)
	if NOWAIT:
		t = 1 
	log.opt(depth=2).debug(f"Waiting for {t} seconds.")
	await asyncio.sleep(t)

@log.catch()
def wait(t):
	if not t:
		t = random.randrange(10,30)
	log.opt(depth=2).debug(f"Waiting for {t} seconds.")
	if NOWAIT:
		t = random.randrange(3,6)
	time.sleep(t)

""" spacer text """
@log.catch()
def sp(length=1):
	o = " "*(int(length))
	return o

""" Clean text from ascii characters and emojis """
@log.catch()
def cleanString(inputString):
	return replace_all(inputString.encode('ascii', 'ignore').decode('ascii'), {
		'"':'',
		"'":'',
		"/":'_',
		"\\" : '_',
		"@" : "_at_",
		
		})

""" replace string with search:value dict """
@log.catch()
def replace_all(text, dic):
	for i, j in dic.items():
		text = text.replace(i, j)
	return text


""" Merge dictionaries """
@log.catch()
def merge_dicts(default: dict, *data: tuple, overwrite=True ):
	if data:
		for d in data:
			for k in d.keys():
				if isinstance(d[k],dict):
					if not k in default:
						default[k] = {}
					default[k] = merge_dicts(default[k],d[k], overwrite=overwrite)
					# for kk in d[k]:
					#   default[k][kk] = d[k][kk]
				else:
					if k in default and default[k] != d[k] and not overwrite: continue
					default[k] = d[k]
	return default  

""" debug helper to print configparser objects """
def print_config(config, return_value=False):
	if return_value: return str({section: dict(config[section]) for section in config.sections()})
	print(str({section: dict(config[section]) for section in config.sections()}))

""" opens a continious stream of the text file and reads all new lines """
def stream_text_file(thefile):
	thefile.seek(0,2)
	while True:
		line = thefile.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line

""" outputs the time in nice format """
@log.catch()
def FormatTime():
	return time.strftime("%x %X",time.localtime())


""" generates a random password """
@log.catch()
def GeneratePassword(self):
	import string,random
	characters = list(string.ascii_letters + string.digits)
	## shuffling the characters
	random.shuffle(characters)

	## picking random characters from the list
	password = []
	for i in range(9):
		password.append(random.choice(characters))

	## shuffling the resultant password
	random.shuffle(password)

	## converting the list to string
	## printing the list
	return "".join(password)