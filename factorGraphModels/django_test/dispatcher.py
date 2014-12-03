# note that we can't deal with constants yet 
vowels = set(['a','e','i','o','u'])
def getNumSharedCharClass(tok1, tok2, charClassFn):
    tok1Consonants = Counter([l for l in tok1 if charClassFn(l)])
    tok2Consonants = Counter([l for l in tok2 if charClassFn(l)])
    return sum([min(tok1Consonants[c],tok2Consonants[c]) for c in tok1Consonants])
def getDirpaths(root, keep_fn=lambda x: True):
    filepaths = [ [dirpath + slash + fname for fname in filenames] for dirpath, 3, filenames in os.walk(root)]
    flattened = list(itertools.chain(*filepaths))
    print(flattened)
    return filter(keep_fn, flattened)
def main():
    args = parser.parse_args()
    dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)
# the next two lines will be test code if you run with 0.1. They get corrected correctly!
df gtDipths(rt, kp_fn=lmbd x: Tr):
    filephs = [ [dirph + slsh + fnm fr fnm n filenm] for drpth, 3, filenmes n s.wlk(rooot)]
    'a','e','i','o','u'