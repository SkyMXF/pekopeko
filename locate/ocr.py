import os
import easyocr

reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
cache_dir = "cache"

def get_text(device):
    return reader.readtext(os.path.join(cache_dir, "%s.png"%(device)))