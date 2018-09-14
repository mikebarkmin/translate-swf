try:
    import Image
except ImportError:
    from PIL import Image
import codecs
import glob
import os
import shutil
import sys
import pytesseract
from subprocess import call
from googletrans import Translator
from tqdm import tqdm

source_files = glob.glob("sources/*.swf")

if not os.path.exists('images'):
    os.mkdir('images')

if not os.path.exists('texts'):
    os.mkdir('texts')


def convert_alpha_to_white(im):
    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    bg_colour = (0, 0, 0)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P'
                                     and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255, ))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im


translator = Translator()

for file_path in tqdm(source_files):
    file_name = file_path.split('/')[-1]

    output_image_name = "{}.png".format(file_name)
    output_image_path = "images/{}".format(output_image_name)
    call(["swfrender", "-r 600", "-o{}".format(output_image_name), file_path])
    shutil.move(output_image_name, output_image_path)

    image = convert_alpha_to_white(Image.open(output_image_path))
    image.save(output_image_path)

    text = pytesseract.image_to_string(image, lang="ell")
    output_text_name = "{}.txt".format(file_name)
    output_text_path = "texts/{}".format(output_text_name)
    with codecs.open(output_text_path, 'w', 'utf-8') as f:
        f.write(text)

    output_text_en_name = "{}_en.txt".format(file_name)
    output_text_en_path = "texts/{}".format(output_text_en_name)
    text_en_translation = translator.translate(text, src="el", dest="en")
    with codecs.open(output_text_en_path, 'w', 'utf-8') as f:
        f.write(text_en_translation.text)
