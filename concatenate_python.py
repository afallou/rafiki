#!usr/bin/env python
import sys, os, subprocess

start_path = os.path.expanduser('~/Documents/cs221_project/django')
out_path = os.path.expanduser('~/Documents/cs221_project/rafiki/django_concat.txt')

for (dirpath, dirnames, filenames) in os.walk(start_path):
    os.chdir(dirpath)
    with open(out_path, 'w') as outfile:
        out = subprocess.check_output(['cat', out_path, '*.py'])
        outfile.write(out)



