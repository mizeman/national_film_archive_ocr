"""Find films, actors and other keywords in scanned archival records.

Author: Michal Zeman; spam@michalzeman.cz
"""

import os
import re
from PIL import Image
from scipy import ndimage
from imageio import imwrite
import pandas as pd
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract\tesseract'

dir_in = "data/in/images"
dir_rotated = "data/in/images_rotated"
files = os.listdir(dir_in)

rows = []
for file in files:
    print(file)  # TODO image processing https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
    path_in = os.path.join(dir_in, file)
    path_out = os.path.join(dir_rotated, re.sub("\.jpg", ".png", file.lower()))
    
    # rotate pages by correct text direction
    try:
        data=pytesseract.image_to_osd(path_in)
    except pytesseract.TesseractError as e:
        print(e)  
        continue  # empty page, TODO test and improve!
    rotation = re.search('(?<=Rotate: )\d+', data).group(0)
    image_rotated = ndimage.rotate(Image.open(path_in), float(rotation) * -1)
    imwrite(path_out, image_rotated)

    # extract Czech text from rotated page
    text = pytesseract.image_to_string(path_out, lang="ces")  # TODO what about Slovak?
    row = {"name": re.sub("\.png", "", file), "text": text}
    rows.append(row)

# find keywords in texts
df = pd.DataFrame(rows)
find = pd.read_excel("data/find.xlsx")  # TODO incorporate Levenshtein distance or similar
keywords = find.groupby("name").keyword.apply(lambda x: "|".join(x))

for name, keyword in keywords.items():
    df[name] = df.text.str.contains(f"({keyword})")
    
# save
df.to_excel("jsem_lepsi_nez_eliska.xlsx")
