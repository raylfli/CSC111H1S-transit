#!/usr/bin/env python
# Generated by BigMap 2. Permalink: http://bigmap.osmz.ru/bigmap.php?xmin=2280&xmax=2295&ymin=2982&ymax=2995&zoom=13&scale=256&tiles=mapnik

import io, urllib.request, datetime, time, re, random, requests
from PIL import Image, ImageDraw
# ^^^^^^ install "python-pillow" package | pip install Pillow | easy_install Pillow

(zoom, xmin, ymin, xmax, ymax) = (13, 2279, 2980, 2296, 2993)
layers = ["https://tile.openstreetmap.org/!z/!x/!y.png"]
attribution = 'Map data (c) OpenStreetMap'
xsize = xmax - xmin + 1
ysize = ymax - ymin + 1
tilesize = 256

resultImage = Image.new("RGBA", (xsize * tilesize, ysize * tilesize), (0,0,0,0))
counter = 0
for x in range(xmin, xmax+1):
	for y in range(ymin, ymax+1):
		for layer in layers:
			url = layer.replace("!x", str(x)).replace("!y", str(y)).replace("!z", str(zoom))
			match = re.search("{([a-z0-9]+)}", url)
			if match:
				url = url.replace(match.group(0), random.choice(match.group(1)))
			print(url, "... ");
			try:
				# req = urllib.request.Request(url, headers={'User-Agent': 'BigMap/2.0'})
				# tile = urllib.request.urlopen(req).read()
				r = requests.get(url, headers={'User-Agent': 'BigMap/2.0'})
				tile = r.content
			except Exception as e:
				print("Error", e)
				continue;
			image = Image.open(io.BytesIO(tile))
			resultImage.paste(image, ((x-xmin)*tilesize, (y-ymin)*tilesize), image.convert("RGBA"))
			counter += 1
			if counter == 10:
				time.sleep(2);
				counter = 0

draw = ImageDraw.Draw(resultImage)
draw.text((5, ysize*tilesize-15), attribution, (0,0,0))
del draw

now = datetime.datetime.now()
outputFileName = "map%02d-%02d%02d%02d-%02d%02d.png" % (zoom, now.year % 100, now.month, now.day, now.hour, now.minute)
resultImage.save(outputFileName)