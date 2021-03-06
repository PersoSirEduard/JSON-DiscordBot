import discord
import json
import random
import urllib.request
from urllib.parse import urlparse
import io
import os
import sys

DISCORD_TOKEN = "discord token"
COMMANDS_JSON = "path to commands.json file"

client = discord.Client()

@client.event
async def on_ready():
	print(client.user,"has connected to Discord!")
	global DISCORD_TOKEN
	DISCORD_TOKEN = "" # Erase the discord token

@client.event
async def on_message(message):
	if message.author == client.user: # Ignore self
		return
	
	commands = getCommands() # Get all commands
	msg = message.content.lower() # Get received message
	
	if msg in commands["uniques"]: # Unique commands
		await message.channel.send(commands["uniques"][msg])
		return
	
		
	for actionName in commands["actions"]: # Loop through all actions
		action = commands["actions"].get(actionName)
		
		if hasIntends(action["intends"], commands, msg): # Verify if required intends per actions are present
			if action["responseType"] == "list": # List type response
				# Expect 'responseFile' and 'responseChoice'
				await action_list(action, commands, msg, message)
				return
			elif action["responseType"] == "text": # Single text response action
				#Expect 'response'
				await action_text(action, commands, msg, message)
				return


async def action_text(action, commands, msg, message):
	#Expect 'response' 
	text = action.get("response", False) # Raw text to send
	responseRate = action.get("responseRate", 1) # Response rate to message command (between 0 to 1)
	if text and random.random() <= responseRate:
		file = False
		for var in action.get("responseFormat", []): #Formatting 
			value = ""
			for f in action["responseFormat"][var]:
				if f == "pipe":
					command = action["responseFormat"][var][f]
					args = command.get("args", [])
					proc = subprocess.Popen(procArgs, stdout=subprocess.PIPE)
					output = proc.communicate()[0]
					value = output.decode('utf-8')
				if f == "exec":
					code = action["responseFormat"][var][f]
					codeString = getFile(code)
					if codeString == "":
						codeString = code
					_locals = locals()
					exec(codeString, globals(), _locals)
					value = _locals["value"]
					file = _locals["file"]
					
				if f == "extract_after_intend":
					intend = action["responseFormat"][var][f]
					arr = msg.split(" ")
					words = hasIntend(commands["intends"][intend], msg).split(" ")
					word = words[len(words)-1]
					value = ' '.join(arr[arr.index(word)+1:]) or ""
				if f == "extract_before_intend":
					intend = action["responseFormat"][var][f]
					arr = msg.split(" ")
					words = hasIntend(commands["intends"][intend], msg).split(" ")
					word = words[0]
					value = ' '.join(arr[:arr.index(word)]) or ""
				if f == "extract_from_intend":
					intend = action["responseFormat"][var][f]
					value = hasIntend(commands["intends"][intend], msg)
				if f == "extract_before_string":
					key = action["responseFormat"][var][f]
					arr = msg.split(" ")
					value = ' '.join(arr[:arr.index(key)]) or ""
				if f == "extract_after_string":
					key = action["responseFormat"][var][f]
					arr = msg.split(" ")
					value = ' '.join(arr[arr.index(key)+1:]) or ""
				if f == "lower":
					key = action["responseFormat"][var][f]
					if key:
						value = value.lower()
						if f == "upper":
							key = action["responseFormat"][var][f]
							if key:
								value = value.upper()
			text = text.replace("%" + var, value)
							
		text = text.replace("$user", message.author.mention)

		if action.get("file", False) or file:
			try:
				if not file:
					file = getDiscordFile(action.get("file", ""))
				if text == "":
					await message.channel.send(file=file)
				else:
					await message.channel.send(text, file=file)
			except Exception as e:
				print("Could not send file.", e)
		else:
			if text != "":
				await message.channel.send(text)	
	else:
		print("Could not find a response string.")
		
async def action_list(action, commands, msg, message):
	# Expect 'responseFile' and 'responseChoice'
	file = action.get("responseFile", False)
	choice = action.get("responseChoice", 0)
	if file:
		if choice == "random": # Get random quote from list
			line = getRandomLine(file).replace("$user", message.author.mention) # Get random line and replace '$user' with a mention of the original message author
			await message.channel.send(line) # Send msg
		else: # Get quote from list by index
			line = getLine(file, choice).replace("$user", message.author.mention) # Get line and replace '$user' with a mention of the original message author
			await message.channel.send(line) # Send msg
	else:
		print("Could not find a valid response file.") # No list file mentionned
		
def getDiscordFile(path):
	fileRequest = isValidUrl(path)
	if fileRequest:
		req = urllib.request.Request(path)
		r = urllib.request.urlopen(req)
		a = urlparse(path)
		f = io.BytesIO(r.read())
		file = discord.File(fp=f, filename=os.path.basename(a.path))
		r.close()
		return file
	else:
		file = discord.File(path)
		return file
	
def getLine(file, index):
	contents = getFile(file) # Get file contents
	lines = contents.splitlines() # Split string into individual lines
	try:
		if int(index) < len(lines) and int(index) >= 0:
			return lines[int(index)] # Return random line
		else:
			print("'{index}' is not between the range of indicies 0 and {max_size}.".format(index=index,max_size=len(lines)))
			return ""
	except Exception as e:
		print("'{}' is not a valid index.".format(index))
		return ""
	
def getRandomLine(file):
	contents = getFile(file) # Get file contents
	lines = contents.splitlines() # Split string into individual lines
	rdmIndex = random.randint(0, len(lines)) # Select random line index
	return lines[rdmIndex] # Return random line
	
def hasIntends(intends, commands, text):
	for intend in intends:
		if not hasIntend(commands["intends"][intend], text):
			return False
	return True

def hasIntend(element, text):
	for x in element:
		if x in text:
			return x
	return False

def getFile(path, aJsonFile=False): # Gets file locally or online
	fileRequest = isValidUrl(path)
	fileContents = ""
	if fileRequest: # Read online file
		fileContents = fileRequest.read().decode('utf-8')
		fileRequest.close()
	else: # Read local file
		try:
			fileRequest = open(path, "r")
			fileContents = fileRequest.read()
			fileRequest.close()
		except Exception as e:
			print("Could not access the local file at '{0}'. {1}".format(path, e))
			return ""
	if aJsonFile: # Parse JSON file
		try:
			jsonParsed = json.loads(fileContents)
			return jsonParsed
		except Exception as e:
			print("Could not parse the JSON file. ", e)
			return {}
	else:
		return fileContents

def isValidUrl(url): # Check if url is valid
	try:
		req = urllib.request.urlopen(url)
		if req.code == 200: # Success
			return req
		else:
			return False
	except ValueError as e:
		return False
	
def getCommands(): # Get commands list online/locally
	return getFile(COMMANDS_JSON, aJsonFile=True)

client.run(DISCORD_TOKEN) # Start Discord bot