# note that we can't deal with constants yet 
def getDirpaths(root, keep_fn=lambda x: True):
    filepaths = [ [dirpath + slash + fname for fname in filenames] for dirpath, _, filenames in os.walk(root)]
    flattened = list(itertools.chain(*filepaths))
    print(flattened)
    return filter(keep_fn, flattened)

def main():
    args = parser.parse_args()
    dirpaths = getDirpaths(os.path.expanduser(args.root), isPythonFile)


# the next two lines will be test code if you run with 0.1. They get corrected correctly!

df gtDipths(rt, kp_fn=lmbd x: Tr):
    filephs = [ [dirph + slsh + fnm fr fnm n filenm] for drpth, _, filenmes n s.wlk(rooot)]
