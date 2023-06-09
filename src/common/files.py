import os,zipfile,shutil,time,tarfile,sys
from typing import *
from common import utils

def get_filename(path: str) -> str:
    return os.path.split(path)[1].split('.')[0]

def is_newer_than(reference, file) -> bool:
    if not os.path.isfile(file):
        print(f'No file {file} found')
        return False
    else:
        return os.stat(reference).st_mtime <= os.stat(file).st_mtime 

def age(file:str) -> int:
    if not os.path.isfile(file):
        print(f'No file {file} found')
        return sys.maxsize
    else:
        return time.time() - os.stat(file).st_mtime 

def read(filepath: str) -> str:
    print(f"Reading file: {os.path.abspath(filepath)}")
    with open( filepath , "r" ) as read:
        text = read.read()
    return text

def read_lines(filepath: str) -> List[str]:
    print(f"Reading file: {os.path.abspath(filepath)}")
    with open( filepath , "r" ) as read:
        text = read.read().splitlines()
    return text

def write(filepath: str, content: str):
    filepath = os.path.abspath(filepath)
    print(f"Writing to file: {filepath}")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath,"w") as w:
        w.write(content)

def load_setfile(filename: str) -> Set[str]:
    print(f'Reading setfile: {os.path.abspath(filename)}')
    return {get_filename(s) for s in read_lines(filename)}

def unpack(zippath: str,files: List[str]) -> None:
    zippath = os.path.abspath(zippath)
    with zipfile.ZipFile(zippath) as z:
        dest = os.path.dirname(os.path.abspath(zippath))
        for f in files:
            if os.path.isfile(f'{dest}\{f}'):
                print(f'File {dest}\{f} already exists - not unpacking.')
                continue
            print(f'Unpacking {f} from {zippath} to {dest}\{f}')
            z.extract(f,dest)

def delete(files: List[str]) -> None:
    for f in files:
        print(f'Removing file {os.path.abspath(f)}')
        os.remove(f)

def move(src, dst):
    print(f"Moving file {src} to {dst}")
    shutil.move(src,dst)
    
def file(name,mode = 'w'):
    os.makedirs(os.path.dirname(name), exist_ok=True)
    return open(name,mode)
def zipped(name):
    if name.endswith('tar.gz'):
        return tarfile.open(name, "r:gz")
    if name.endswith('tar.bz2'):
        return tarfile.open(name, "r:bz2")
    elif name.endswith('zip'):
        return zipfile.ZipFile(name)
    else:
        print(f'Error reading zipped file: {name}, unknown extension')
        return None

def zipped_members(fileobj):
    if utils.has_method(fileobj, 'getmembers'):
        return fileobj.getmembers()
    if utils.has_method(fileobj, 'infolist'):
        return fileobj.infolist()
    else:
        raise Exception('Unknown file object type')

def is_zipped_file(info):
    if utils.has_method(info, 'isfile'):
        return info.isfile()
    if utils.has_method(info, 'is_dir'):
        return not info.is_dir()
    else:
        raise Exception('Unknown file object type')
    
def zipped_name(info):
    if type(info) is zipfile.ZipInfo:
        return info.filename
    if type(info) is tarfile.TarInfo:
        return info.name
    else:
        raise Exception('Unknown file object type')
    
def open_zipped(fileobj, name):
    if utils.has_method(fileobj, 'extractfile'):
        return fileobj.extractfile(name)
    if utils.has_method(fileobj, 'open'):
        return fileobj.open(name)
    else:
        raise Exception('Unknown file object type')