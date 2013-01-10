#!/usr/bin/env python
'''
initially populates the directory with a set of structures determined by atat and then run a sprecified script in each directory.'''
import os, time, sys
from optparse import OptionParser

parser = OptionParser(usage='startatat.py [-m] [COUNT] [-r] [command]',
                      version='0.1')
parser.add_option('-m',
                  nargs=0,
                  help = 'run mmaps instead of maps')

parser.add_option('-n',
                  nargs=1,
                  help = 'number of structures to generate')

parser.add_option('-r',
                  nargs=1,
                  help = 'run command after structures are generated')

options,args = parser.parse_args()

if os.path.exists('maps_is_running'):
    print('Detected maps_is_running. attempting to stop it.')
    open('stop','w').close()
    time.sleep(10)
    if os.path.exists('maps_is_running'):
        os.unlink('maps_is_running')
    
if options.m is None:
    os.system('maps -d &')
else:
    os.system('mmaps -d &')

if options.n is None:
    COUNT = 10
else:
    COUNT = int(options.n)

counter = 0

while counter <= COUNT:

    if not os.path.exists('ready'):
        print 'touching ready: %i' % counter
        open('ready','w').close()
        counter += 1
    # give maps enough time to make a new figure
    time.sleep(5)

# now stop the(m)maps daemon
open('stop','w').close()

if options.r is not None:
    os.system('foreachdir.py wait %s' % options.r)

