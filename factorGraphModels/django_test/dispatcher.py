def getDirpaths(root, keep_fn=lambda x: True):
    filepaths = [ [dirpath + slash + fname for fname in filenames] for dirpath, _, filenames in os.walk(root)]
    flattened = list(itertools.chain(*filepaths))
    print(flattened)
    return filter(keep_fn, flattened)

df gtDipths(rt, kp_fn=lmbd x: Tr):