#!/usr/bin/env python
'''
Script to create an excel spreadsheet containing the ATAT data

Sheet 1 - Summary data
id1 composition formation_energy bulk_modulus

Sheet 2 - Unit cell parameters
id1 a b c alpha beta gamma volume sxx syy szz sxy syz sxz

Sheet 3 - Atomic positions
id1 atomid species x y z fx fy fz

Sheet 4 - Computational details
id1 par1 par2 par3
'''

from atat import *
from atat.atat_eos import *
import glob, os
import xlwt, xlrd
import xlutils.copy 
import numpy as np
from Scientific.Geometry import Vector
from pyspglib import spglib

base, curdir = os.path.split(os.getcwd())
XLS = curdir + '.xls'
if os.path.exists(XLS):
    print('reading existing file')
    rb = xlrd.open_workbook(XLS)
    wbk = xlutils.copy.copy(rb)
    sh0 = wbk.get_sheet(0)
    sh1 = wbk.get_sheet(1)
    sh2 = wbk.get_sheet(2)
    sh3 = wbk.get_sheet(3)
else:
    wbk = xlwt.Workbook()
    sh0 = wbk.add_sheet('summary')
    for i, label in enumerate(['id', 'composition', 'space group',
                               'natoms', 'formation energy (eV/atom)',
                               'Bulk modulus (GPa)',
                           'magnetic moment (bohr-magneton)']):
        sh0.write(0, i, label)
    sh1 = wbk.add_sheet('unit-cell')
    for i, label in enumerate(['id', 'a (ang)', 'b', 'c', 'alpha (deg)', 'beta', 'gamma',
                               'volume (ang^3)', 'sxx (GPa)', 'syy', 'szz', 'sxy',
                               'syz', 'sxz']):
        sh1.write(0, i, label)
    sh2 = wbk.add_sheet('positions')
    for i,label in enumerate(['id','atom-id', 'chemical-symbol', 'x (ang)', 'y', 'z',
                    'fx (eV/ang)', 'fy', 'fz']):
        sh2.write(0, i, label)
    sh3 = wbk.add_sheet('computational-parameters')
    params = ['input_params',
              'int_params',
              'float_params',
              'exp_params',
              'string_params',
              'list_params',
              'dict_params',
              'special_params']
    # here we write out the sorted list of keys for each parameter
    v = Vasp()
    labels = ['id']
    for p in params:
        labels += sorted(getattr(v,p).keys())
    for i,label in enumerate(labels):
        sh3.write(0,i, label)
    print('created new file.')

with open('fit.out') as fh:
    for line in fh:
        fields = line.split()
        X = float(fields[0])
        formation_energy = float(fields[1])
        id1 = fields[-1]
        
        # get number of rows. since we use 0-indexing, the next row is NROWS
        NROWS0 = len(sh0.get_rows())
        NROWS1 = len(sh1.get_rows())
        with jasp(id1) as calc:
            atoms = calc.get_atoms()
            composition = atoms.get_chemical_symbols(reduce=True)
            spacegroup = spglib.get_spacegroup(atoms, symprec=1e-5)

            natoms = len(atoms)
            x, V0, e0, B = analyze_eos()

            magmom = atoms.get_magnetic_moment()
            # now we want to write out a row of
            data = [id1, composition, spacegroup, natoms, formation_energy, B, magmom]
            for i,d in enumerate(data):
                sh0.write(NROWS0, i, d)

            # now for sheet 1 - unit cell parameters
            uc = atoms.get_cell()
            A = Vector(uc[0,:])
            B = Vector(uc[1,:])
            C = Vector(uc[2,:])
            a = A.length()
            b = B.length()
            c = C.length()
            alpha = B.angle(C)*180./np.pi
            beta = A.angle(C)*180./np.pi
            gamma = B.angle(C)*180./np.pi
            volume = atoms.get_volume()

            stress = atoms.get_stress()
            if stress is not None:
                sxx, syy, szz, sxy, syz, sxz = stress
            else:
                sxx, syy, szz, sxy, syz, sxz = [None, None, None, None, None, None]

            data = [id1, a, b, c, alpha, beta, gamma, volume, sxx, syy, szz, sxy, syz, sxz]
            for i, d in enumerate(data):
                sh1.write(NROWS1, i, d)

            # now we write each position out.
            forces = atoms.get_forces()
            for atom_index, atom in enumerate(atoms):
                NROWS2 = len(sh2.get_rows())
                f = forces[atom_index]
                data = [id1, atom_index, atom.symbol, atom.x, atom.y, atom.z, f[0], f[1], f[2]]

                for i,d in enumerate(data):
                    sh2.write(NROWS2, i, d)

            # finally the computational parameters
            data = [id1]
            NROWS3 = len(sh3.get_rows())
            for p in params:
                d = getattr(calc, p)
                keys = sorted(d.keys())
                for k in keys:
                    data.append(d[k])
            for i,d in enumerate(data):
                if i == 0:
                    sh3.write(NROWS3, i, d)
                else:
                    sh3.write(NROWS3, i, repr(d))
                
        wbk.save('atat.xls')


