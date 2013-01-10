#!/usr/bin/env python
'''
run command on each directory that contains file, recursively

foreachdir.py file cmd
'''

import commands, os, sys

target = sys.argv[1]
command = sys.argv[2]

CWD = os.getcwd()
for dirpath, dirnames, filenames in os.walk('.'):

    if target in filenames:
        try:
            os.chdir(dirpath)
            status,output = commands.getstatusoutput(command)
            print status, output
        except:
            print('Caught exception in {0}'.format(CWD))
        finally:
            os.chdir(CWD)
