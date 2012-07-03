#!/usr/bin/env python
'''
python substitute for cleanvasp with an option to deep clean an atat directory which gets rid of everything but the str.out file!.
'''
import glob, os

def cleanvasp():
    files_to_remove = ['CHG','CHGCAR', 'WAVECAR', 'POTCAR',
                       'EIGENVAL', 'IBZKPT', 'PCDAT', 'XDATCAR',
                       'INCAR', 'POSCAR', 'KPOINTS',
                       'CONTCAR', 'OSZICAR', 'OUTCAR', 'vasp.out',
                       'DOSCAR']

    for f in files_to_remove:
        if os.path.isfile(f):
            os.unlink(f)
    print 'cleaned %s' % os.getcwd()

def deep_clean():
    'remove everything from the directory but str.out'
    if not os.path.exists('str.out'):
        raise Exception, 'You are not in an atat directory! this will delete everything here! Exiting befor you do any damage.'

    files = glob.glob('*')

    for f in files:
        if os.path.isfile(f) and f != 'str.out':
            os.unlink(f)
    print 'deep-cleaned %s' % os.getcwd()

if __name__ == '__main__':

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-d", "--deepclean",
                      nargs=0,
                      help="deep clean - remove everything but str.out")

    (options, args) = parser.parse_args()

    if options.deepclean is not None:
        deep_clean()
    else:
        cleanvasp()
