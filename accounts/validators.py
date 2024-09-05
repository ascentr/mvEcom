import os
from django.core.exceptions import ValidationError

def allow_only_images_validator(value):
	ext = os.path.splitext(value.name)[1] # e.g cover_image.jpg (ext = jpg)
	print(ext)
	valid_extentions = ['.jpeg' , '.jpg' ,'.png' , '.gif' ]

	if not ext.lower() in valid_extentions:
		raise ValidationError('Unsupported File Type - Allowed extentions are : ' + str(valid_extentions))