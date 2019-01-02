from flask import Flask, render_template, request, jsonify, send_file
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_cors import CORS, cross_origin
from urllib.request import urlopen,build_opener,HTTPCookieProcessor
from http.cookiejar import CookieJar
from PIL import Image, ImageChops, ExifTags
import xmltodict
import json
import requests
import re
import os

app = Flask(__name__)
cors = CORS(app)

photos = UploadSet('photos', IMAGES)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

@app.route("/imagesearch", methods=['POST'])
@cross_origin()
def imageLookup():
    if 'queryImg' in request.files:
        img_path = './static/img/lookupImg.jpg'
        if os.path.exists(img_path):
            os.remove(img_path)

        # shutil.rmtree('static/img')
        filename = photos.save(request.files['queryImg'], folder=None, name='lookupImg.jpg')

        cj = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')]

        filePath = './static/img/lookupImg.jpg'
        searchUrl = 'http://www.google.hr/searchbyimage/upload'
        multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
        response = requests.post(searchUrl, files=multipart, allow_redirects=False)
        fetchUrl = response.headers['Location']

        sourceCode = opener.open(fetchUrl).read().decode('utf-8')

        links = re.findall(r'<div class="rc"><div class="r"><a href="(.*?)"',sourceCode)

        return(jsonify(links))

@app.route("/ela", methods=['POST'])
@cross_origin()
def ela():
    if 'queryImg' in request.files:
        ORIG = './static/img/elaImg.jpg'
        TEMP = './static/img/temp.jpg'
        SCALE = 10

        if os.path.exists(ORIG):
            os.remove(ORIG)
        if os.path.exists(TEMP):
            os.remove(TEMP)
        if os.path.exists('./imageAnalysis/img/output.jpg'):
            os.remove('./imageAnalysis/img/output.jpg')

        filename = photos.save(request.files['queryImg'], folder=None, name='elaImg.jpg')

        original = Image.open(ORIG)
        original.save(TEMP, quality=75)
        temporary = Image.open(TEMP)

        diff = ImageChops.difference(original, temporary)
        d = diff.load()
        WIDTH, HEIGHT = diff.size
        for x in range(WIDTH):
            for y in range(HEIGHT):
                d[x, y] = tuple(k * SCALE for k in d[x, y])

        diff.save('./imageAnalysis/img/output.jpg')
        return (send_file('img/output.jpg', mimetype='image/jpg'))

    return 'ERROR'

@app.route("/metadata", methods=['POST'])
@cross_origin()
def metadata():
    if 'queryImg' in request.files:
        in_path = './static/img/metadataIn.jpg'

        if os.path.exists(in_path):
            os.remove(in_path)

        filename = photos.save(request.files['queryImg'], folder=None, name='metadataIn.jpg')

        # open input file
        img = Image.open(in_path)
        pairs = dict()

    	# if img format supports EXIF
        if (img._getexif()):
            # fetch exif object
            exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS}

    		# to do: can compare original data/create date with modifiy data
    		# parse MakerNote or not, e.g. ray.jpg
            for x in exif:
                if isinstance(exif[x], bytes):
    		    	# show binary data: utf-8 utf-16 utf-32 ascii raw
    		    	# output = "" + x + ':' + exif[x].decode('utf-16') + "\n"
    		    	# output = "" + x + ':' + str(exif[x]) + "\n"

    				# if output dict to file
    		    	# output = "" + x + " : (Binary data " + str(len(str(exif[x]))) + " bytes)\n"
                    pairs[x] = "(Binary data " + str(len(str(exif[x]))) + " bytes)"
                else:
    		    	# if output dict to file
    		    	# output = "" + x + ' : ' + str(exif[x]) + "\n"
                    pairs[x] = exif[x]

            output = "" + str(json.dumps(pairs, indent=4))
            return output

    	# if img format cannot support EXIF, output all XMP
        else:
            info = img.info

            for key, value in info.items():
                if isinstance(value, bytes):
                    pairs[key] = "(Binary data " + str(len(value)) + " bytes)"
    				# output = "" + str(key) + " : (Binary data " + str(len(str(value))) + " bytes)\n"
                else:
                    if "xmp" in key:
                        xmp = str(info[key])
                        d = xmltodict.parse(xmp)

                        output = "" + json.dumps(d, indent=4) + "\n"
                    else:
                        pairs[key] = value
    					# output = "" + str(key) + ' : ' + str(value) + "\n"

            output = "" + json.dumps(pairs, indent=4) + "\n"
            return output

    return 'ERROR'

@app.route("/elascore", methods=['POST'])
@cross_origin()
def elascore():
    if 'queryImg' in request.files:
        ORIG = './static/img/elaScoreImg.jpg'
        TEMP = './static/img/elaScoreTemp.jpg'
        SCALE = 10

        if os.path.exists(ORIG):
            os.remove(ORIG)
        if os.path.exists(TEMP):
            os.remove(TEMP)
        if os.path.exists('./imageAnalysis/img/scoreOutput.jpg'):
            os.remove('./imageAnalysis/img/scoreOutput.jpg')

        filename = photos.save(request.files['queryImg'], folder=None, name='elaScoreImg.jpg')

        original = Image.open(ORIG)
        original.save(TEMP, quality=75)
        temporary = Image.open(TEMP)

        diff = ImageChops.difference(original, temporary)
        d = diff.load()
        WIDTH, HEIGHT = diff.size
        for x in range(WIDTH):
            for y in range(HEIGHT):
                d[x, y] = tuple(k * SCALE for k in d[x, y])

        diff.save('./imageAnalysis/img/scoreOutput.jpg')

        im = Image.open('./imageAnalysis/img/scoreOutput.jpg').convert('L')
        pixels = im.getdata()

        # 0 (pitch black) and 255 (bright white)
        black_thresh = 20
        pixels_length = len(pixels)
        nblack = 0

        for pixel in pixels:
            if pixel < black_thresh:
                nblack += 1

        if (100 - ((pixels_length - nblack) / pixels_length * 100)) >= 90:
            return 'A'
        elif (100 - ((pixels_length - nblack) / pixels_length * 100)) >= 80:
            return 'B'
        elif (100 - ((pixels_length - nblack) / pixels_length * 100)) >= 70:
            return 'C'
        elif (100 - ((pixels_length - nblack) / pixels_length * 100)) >= 60:
            return 'D'
        else:
            return 'F'

        # return ("Pixel Change Percentage: {0:.2f}%".format((pixels_length - nblack) / pixels_length * 100))

    return 'ERROR'
