#!/usr/bin/env python
from optparse import OptionParser
from atat import  *
from jasp import *
from ase.utils.eos import *
import os, sys
from ase.units import GPa
'''
sets up the equation of state calculations we want for atat/reax in a directory where there is a str.out

atat_eos.py 2   #setup basic EOS in directory 2
atat_eos.py --factors 8,9,10 2  #add strains of 8,9,10% to the EOS calculations

atat_eos.py --analyze 2   #plot EOS parameters

afterwards, you can submit the jobs like this:
foreachdir.py wait run_atat_vasp.py
'''

def setup_eos(factors=[-6,-4,-2,0,2,4,6], force=False):
    '''sets up the EOS jobs from the relaxed geometry

    factors is a list of %strains to apply to the relaxed unit cell
    force is a flag that determines whether existing files are overwritten. usually, if the directories are detected, nothing new is done.

    This function must be called within an atat directory.
    '''

    if os.path.exists('error'):
        return "error"

    if not os.path.exists('str.out'):
        raise Exception, 'Not in an atat directory. no str.out found'

    if not os.path.exists('str_relax.out'):
        return 'Main job has not completed yet. Please try again later.'

    # Now we create the EOS jobs
    atoms = str2atoms('str_relax.out')
    uc = atoms.get_cell()
    for f in factors:
        factor = 1 + f/100.

        atoms.set_cell(uc*factor**(1./3.))

        calcdir = 'eos-exp/f%+i' % f
        if os.path.isdir(calcdir):
            # we have made this directory before
            if force:
                pass
            else:
                continue

        print calcdir, atoms.get_volume()
        CWD = os.getcwd()
        if not os.path.isdir(calcdir):
            os.makedirs(calcdir)
        os.chdir(calcdir)
        atoms2str(atoms)
        open('wait','w')

        # find vasp.wrap
        lines = []
        for vw in ['../vasp.wrap',
                   '../../vasp.wrap',
                   '../../../vasp.wrap']:
            if os.path.exists(vw):
                f = open(vw, 'r')
                lines = f.readlines()
                f.close()
                break

        # now write out vasp.wrap for the EOS where no relaxation occurs
        f = open('vasp.wrap','w')
        for i,line in enumerate(lines):
            if line.startswith('ISIF'):
                line = 'ISIF = 2\n'
            f.write(line)
        f.close()
        os.chdir(CWD)
    return 'setup complete'

def analyze_eos(plot=False):
    '''make plot of EOS

    This may trigger calculations to be submitted to the queue. You should not run this function before the directories for the EOS are setup.

    must be called from within an atat directory'''
    if not os.path.isdir('eos-exp'):
        return None

    CWD = os.getcwd()
    head, wd = os.path.split(CWD)

    V,E = [],[]

    os.chdir('eos-exp')
    for d in os.listdir('.'):
        if (os.path.exists('%s/energy' % d)
            and not os.path.exists('%s/error' % d)):
            #print os.getcwd()+'/'+d
            with jasp(d) as calc:
                atoms = calc.get_atoms()
                V.append(atoms.get_volume())
                E.append(atoms.get_potential_energy())
    os.chdir(CWD)

    if (len(V) < 5 or len(E) < 5):
        return None

    eos = EquationOfState(V, E)

    try:
        v0, e0, B = eos.fit()
        CWD = os.getcwd()
        base,d = os.path.split(CWD)
        #print '| %s | %1.3f | %1.1f |' % (d, v0/len(atoms), B/GPa)
    except ValueError, e:
        print e
        return

    p = eos.plot(show=False)
    ax = p.gca()
    # replace axis with proper angstrom symbol
    ax.set_xlabel('volume ($\AA^3$)')
    ax.set_title('E: %1.3f eV, V: %1.2f $\AA^3$, B: %1.1f GPa\nworking dir = %s' % (e0,
                                                                  v0,
                                                                  B/GPa,wd))
    #ax.text(v0,0.5*(np.min(E) + np.max(E)),'working dir = %s' % wd)
    p.tight_layout()
    p.savefig('eos.png')

    if plot:
        import matplotlib.pyplot as plt
        plt.show()
        return (p, v0/len(atoms), e0, B/GPa)
    else:
        return (None, v0/len(atoms), e0, B/GPa)


if __name__ == '__main__':
    '''
    Setup jobs in directory 0. Run as many times as you want, it should only create directories once

      atat_eos.py 0

    recreate jobs for directory 0, even if they already exist.
      atat_eos.py --force 0

    create and run jobs in directory 2
      atat_eos.py --run 2

    '''

    parser = OptionParser(usage='atat_eos.py [--force] [--factors] [a,b,c] [--run] [--analyze]  dirs',
                      version='0.1')

    parser.add_option('--factors',
                      nargs=1,
                      help='comma-separated list of strains on unit cell for eos. strains should be integers in %, e.g. 6 means 6% expansion. this only sets up the directories, it does not run the calculations.')

    parser.add_option('--force',
                      nargs=0,
                      help='force setup to overwrite existing directories')

    parser.add_option('--run',
                      nargs=0,
                      help='run jobs')

    parser.add_option('--analyze',
                      nargs=0,
                      help='run equation of state')
    parser.add_option('--plot',
                      nargs=0,
                      help='show EOS plot')

    parser.add_option('--status',
                      nargs=0,
                      help='show status of eos')

    options,args = parser.parse_args()

    CWD = os.getcwd()

    if options.force is not None:
        force = True
    else:
        force = False

    if options.plot is not None:
        plot = True
    else:
        plot = False


    if options.status is not None:
        if len(args) > 10:
            print '#+ATTR_LaTeX: longtable'
        print '#+tblname: atat-eos-status'
        print '|{0:^25}|{1:^25}|'.format('directory','status')
        print '|' + 52*'-'
        for arg in args:
            eos_dir = os.path.join(arg,'eos-exp')
            if not os.path.isdir(eos_dir):
                print '|{0:^25}|{1:^25}|'.format(eos_dir,'no eos-exp')
            else:
                edirs = os.listdir(eos_dir)
                for ed in edirs:
                    path = os.path.join(eos_dir,ed)
                    if not os.path.isdir(path):
                        continue
                    if os.path.exists(os.path.join(path,'wait')):
                        print '|{0:^25}|{1:^25}|'.format(path,'waiting')
                    elif os.path.exists(os.path.join(path,'error')):
                        print '|{0:^25}|{1:^25}|'.format(path,'error')
                    elif os.path.exists(os.path.join(path,'jobid')):
                        f = open(os.path.join(path,'jobid'))
                        jobid = f.readline().strip()
                        f.close()
                        s = '[[shell:qstat -f {0}][{0}]]'.format(jobid)
                        print '|{0:^25}|{1:^25}|'.format(path,s)
                    elif os.path.exists(os.path.join(path,'energy')):
                        print '|{0:^25}|{1:^25}|'.format(path,'done')

                    else:
                        print '|{0:^25}|{1:^25}|'.format(path,'unknown')

        sys.exit()

    if options.analyze is not None:
        print '| directory | V0 (Ang^3/atom) | E0 (eV) | B (GPa) |'
        print '|-'


        for arg in args:
            if os.path.isdir(arg):
                os.chdir(arg)
            else:
                continue

            out = analyze_eos(plot)
            if out is not None:
                p,v0,e0,B = out
                print '| %s | %1.2f | %1.3f | %1.1f |' % (arg, v0, e0, B)
            else:
                print '| %s | - | - | - |' % (arg)
            os.chdir(CWD)
    else:
        if options.factors is None:
            factors = [6, 4, 2, 0, -2, -4, -6]
        else:
            factors = [int(x) for x in options.factors.split(',')]

        for arg in args:
            os.chdir(arg)
            print arg, setup_eos(factors, force)
            os.chdir(CWD)

    if options.run is not None:
        os.system('foreachdir.py wait run_atat_vasp.py')
