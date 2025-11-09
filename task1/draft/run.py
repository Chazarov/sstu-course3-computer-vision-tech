from PIL import Image
from PIL.ExifTags import TAGS

print("start")

img = Image.open('sourse/image.png')
exif = img.getexif()

for tag_id, value in exif.items():
    tag = TAGS.get(tag_id, tag_id)
    print(f"{tag}: {value}")

print("end")