#!usr/bin/env python
import sys, os, subprocess

start_path = os.path.expanduser('~/Documents/cs221_project/django')
out_path = os.path.expanduser('~/Documents/cs221_project/rafiki/django_concat.txt')

for (dirpath, dirnames, filenames) in os.walk(start_path):
    with open(out_path, 'a') as out_file:
        try:
            out = subprocess.check_output('cd ' + dirpath + ' && cat *.py', shell=True)
            out_file.write(out)
        # *.py returns nothing
        except Exception:
            pass
