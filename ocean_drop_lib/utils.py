"""

    Utils Module


"""
import math
import os
import logging
import hashlib
import re

from web3 import Web3

logger = logging.getLogger('ocean_drop.utils')

BYTES_PER_KB = 1000

def read_file_list(folder, file_list, total_size):
    logger.debug(f'Scanning folder {folder}')
    for root, dirs, files in os.walk(folder):
        if len(files) == 0 and len(dirs) == 0:
            stat = os.lstat(root)
            file_list.append({
                'is_file': False,
                'folder':root,
                'mtime': stat.st_mtime,
                'size': 0,
            })
        for file in files:
            filename = os.path.join(root, file)
            stat = os.lstat(filename)
            md5_hash = hash_file(filename)
            relative_filename = get_relative_path(folder, root, filename)
            total_size = total_size + stat.st_size
            file_list.append({
                'is_file': True,
                'filename': filename,
                'relative_filename': relative_filename,
                'folder':root,
                'mtime': stat.st_mtime,
                'size': stat.st_size,
                'md5_hash': md5_hash,
            })

    file_list = sorted(file_list, key = lambda k:k['mtime'])
    return (file_list, total_size)

def get_relative_path(base_folder, folder, filename):
    base_folder_abs_path = os.path.abspath(base_folder)
    folder_abs_path = os.path.abspath(folder)
    relative_path = folder_abs_path[len(base_folder_abs_path):]
    base_filename = os.path.basename(filename)
    relative_filanme = re.sub('^/', '', os.path.join(relative_path, base_filename))
    return relative_filanme

def hash_file(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def show_size_as_text(size):
    result = f'{size} Bytes'
    items = [
        (BYTES_PER_KB, 'KB'),
        (math.pow(BYTES_PER_KB, 2), 'MB'),
        (math.pow(BYTES_PER_KB, 3), 'GB'),
        (math.pow(BYTES_PER_KB, 4), 'TB'),
    ]

    for item in items:
        if size < item[0]:
            break
        format_size = size / item[0]
        result = f'{format_size:.2f} {item[1]}'

    return result

def generate_listing_checksum(nonce, drop_secret):
    return Web3.toHex(Web3.sha3(text=f'{nonce}{drop_secret}'))