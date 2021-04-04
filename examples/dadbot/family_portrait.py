from PIL import Image
import requests

if (len(message.mentions) >= 2):
	img = Image.open("family_portrait.jpg")
	userAvatar1 = Image.open(requests.get(message.mentions[0].avatar_url, stream=True).raw)
	userAvatar2 = Image.open(requests.get(message.mentions[1].avatar_url, stream=True).raw)
	
	userAvatar1 = userAvatar1.resize((120, 120))
	userAvatar2 = userAvatar2.resize((120, 120))
	
	img.paste(userAvatar1, (325 - 60, 360 - 60), userAvatar1)
	img.paste(userAvatar2, (477 - 60, 242 - 60), userAvatar2)
	
	with io.BytesIO() as image_binary:
		img.save(image_binary, 'PNG')
		image_binary.seek(0)
		file = discord.File(fp=image_binary, filename='image.png')
else:
	value = "A family picture would be nice, but with who? I need two people to volunteer!"