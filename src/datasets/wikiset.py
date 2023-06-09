NOT_FOUND_MSG = '''
    Wiki_727K dataset not found!
    Make sure the files:
    * wiki_727K.tar.bz2
    * wiki_test_50.tar.bz2

    Are placed in the /data folder in root directory
    The download link used to aquire the dataset is: (may not be working at the time of reading)
    https://www.dropbox.com/sh/k3jh0fjbyr0gw0a/AADzAd9SDTrBnvs1qLCJY5cza?dl=0
    '''
from datasets import DATASET_DIR, TMP_DIR
from common import files, stage
import numpy as np
import tensorflow_hub as hub
import tensorflow_text
import os, shutil
from models import sentence_bert as sbert

def get(variant = None):
    if not check():
        return None
    elif variant == 'full':
        return os.path.abspath(os.path.join(DATASET_DIR,'wiki_727K.tar.bz2'))
    elif variant == 'dev':
        return os.path.abspath(os.path.join(DATASET_DIR,'wiki_dev.zip'))
    elif variant == 'test':
       return os.path.abspath(os.path.join(DATASET_DIR,'wiki_test.zip'))
    else: return os.path.abspath( os.path.join(DATASET_DIR,'wiki_test_50.tar.bz2'))

def check():
    bigdataset = os.path.abspath(os.path.join(DATASET_DIR,'wiki_727K.tar.bz2'))
    smallset =os.path.abspath( os.path.join(DATASET_DIR,'wiki_test_50.tar.bz2'))

    b_found = os.path.isfile(bigdataset)
    s_found = os.path.isfile(smallset)

    print(f'{bigdataset} found: {b_found}')
    print(f'{smallset} found: {s_found}')
    if not (b_found and s_found):
        print(NOT_FOUND_MSG)
    return b_found or s_found

def get_raw_lines(dsfile, filename):
    with files.zipped(dsfile) as wiki_ds:
        members = [m.name for m in wiki_ds.getmembers() if m.isfile()]
        if filename not in members:
            print(f'File {filename} not found in archive {dsfile}')
            return None
        else:
            return [l.decode('utf-8') for l in wiki_ds.extractfile(filename).readlines()]

def get_unsegmented_lines(dsfile, filename):
    return [l for l in get_raw_lines(dsfile,filename) if not l.startswith('===') and not l.startswith('***')]


@stage.measure("Making sentence embeddings")
def make_embeddings(infile, outfile, embedder = 'trans', trunc = None):
    sentence_bert = sbert.get(embedder)
    with files.zipped(infile) as wiki_ds:
        if trunc == None:
            members = [m for m in files.zipped_members(wiki_ds) if files.is_zipped_file(m)]
        else:
            members = [m for m in files.zipped_members(wiki_ds)[:trunc] if files.is_zipped_file(m)]
        bar = stage.ProgressBar("Embedding sentences",len(members))
        for name in members:
            bar.update(files.zipped_name(name))
            reader = files.open_zipped(wiki_ds,name)
            lines = [l.decode('utf-8') for l in reader.readlines()] # decode lines
            lines = [l for l in lines if not l.startswith('***')] # filter special makers
            sentences = [l for l in lines if not l.startswith('===')]
            div_i = np.array([i for i,line in enumerate(lines) if line.startswith('===')] + [len(lines)])
            div_t = np.repeat(np.arange(len(div_i)-1),np.diff(div_i)-1)
            embeddings = sentence_bert(sentences)
            assert len(div_t) == len(embeddings), f'{len(div_t)} != {len(embeddings)}'
            np.save(files.file(TMP_DIR+'/'+files.zipped_name(name)+'_seg.npy','wb'),div_t)
            np.save(files.file(TMP_DIR+'/'+files.zipped_name(name)+'_emb.npy','wb'),embeddings)
            #print(f'{name.name} : {div_i} : {len(sentences)} = {len(div_t)} : {embeddings.shape}')
        bar.end()
    shutil.make_archive(outfile,'zip',root_dir=TMP_DIR,base_dir='.')
    os.replace(outfile+'.zip',outfile+'.npz')
    shutil.rmtree(TMP_DIR)


    


