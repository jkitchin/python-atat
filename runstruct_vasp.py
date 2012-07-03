#!/usr/bin/env python
'''
This is a python replacement of runstruct_vasp.

The purpose is multifold:
1. learn what runstruct_vasp does
2. modularize the functionality to better integrate with python

4/5/2012
'''

import os



def runstruct_vasp(wrapfile='vasp.wrap',
                   command_prefix=None,
                   preserve='True',
                   lookup=False,
                   no_generate=False,
                   no_run=False,
                   extract=False,):





if __main__ == '__name__':
    import optparse

    if os.path.exists('~/.ezvasp.rc'):
        os.system('~/.ezvasp.rc')
    else:
        os.system('ezvasp')
