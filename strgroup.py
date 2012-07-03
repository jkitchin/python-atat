#!/usr/bin/env python

'''
Get the space group for str.out
'''

from atat import str2atoms
from symmetry.sgroup import SpaceGroup

atoms = str2atoms('str.out')

print SpaceGroup(atoms).GetSpaceGroup()
