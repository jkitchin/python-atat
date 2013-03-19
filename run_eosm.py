#!/usr/bin/env python
'''
script to run in an ATAT directory

The script automatically sets up a VASP calculation, sets the magnetic moments, and computes an equation of state. You run this script inside an ATAT directory.

When you run this in the queue, VASP is run.
When you run this on the login node, a job is submitted.

Only serial jobs are supported. it will take some effort to get parallel or multiprocessing integrated. It might be possible to set this in vaspwrap.py

Example usage with ATAT integration
startatat.py [-m] [COUNT] -r run_eosm.py

Future features:
define a function for estimating the volume for cases where Vegard's law is known to be inadequate.
'''

import os, sys
if 'PBS_O_WORKDIR' in os.environ:
    #use a non-X requiring background in case a matplotlib plot is made
    import matplotlib
    matplotlib.use('Agg')

from atat import *
from jasp import *
from jasp.jasp_eos import *
import json

# we need to find vaspwrap.py. Here is an example
'''
# experimental atomic volume to use for Vegard's law in estimating the
# initial volume
VOL = {'Al':(4.05**3)/4.0,
       'Ni':(3.52**3)/4}

# initial guesses for magnetic moments
MAGMOMS = {'Ni':2.5,
           'Fe':2.0,
           'Co':2.0}

# use these parameters in the VASP calculations
vasppars = {'encut':350,
            'xc':'PBE',
            'prec':'high',
            'ispin':2,
            'ismear':2,
            'sigma':0.1}

# KPT settings
KPPRA = 2000
'''

found = False
for vwp in ['../../vaspwrap.py', '../vaspwrap.py', 'vaspwrap.py']:
    # execute each one. local wrapper has precedent.
    if os.path.exists(vwp):
        found = True
        execfile(vwp)
if not found:
    raise IOError, "no vaspwrap.py found!"
    
##################################################################
###### script below here.

# string template to print eventually
s = '{cwd}: E={energy:1.3f} eV  V={volume:1.3f} A^3 B={B:1.0f} GPa M={M:1.2f} mu'
base,cwd = os.path.split(os.getcwd())

def run():
    # look for atat.json It contains all the data we want. If it
    # exists, just return so no new calculations get created.
    if os.path.exists('atat.json'):
        with open('atat.json') as f:
            data = json.loads(f.read())
            data['cwd'] = cwd
            print s.format(**data)
            return data

    # get the atoms object from str.out
    atoms = str2atoms()

    # adjust volume according to Vegard's law and set the magnetic moments
    vol = 0.0
    for atom in atoms:
        atom.magmom = MAGMOMS.get(atom.symbol, 0.0)
        vol += VOL[atom.symbol]
    atoms.set_volume(vol)

    kpts = get_kpts_from_kppra(atoms, KPPRA)

    # now we get the equation of state
    with jasp('.',
              kpts=kpts,
              atoms=atoms,
              **vasppars) as calc:
        calc.set_nbands(f=2)
        
        try:
            data = calc.get_eos()
        except:
            with open('error', 'w') as f:
                f.write('Error getting the equation of state')

        M = atoms.get_magnetic_moment()
        B = data['step2']['avgB']
            
        with open('energy', 'w') as f:
            f.write(repr(data['step3']['potential_energy']))

    # now we are done, we can delete some files
    for f in ['wait', 'jobid', 'error']:
        if os.path.exists(f):
            os.unlink(f)

    # create json data to store
    jsondata = {'cwd':cwd,
                'energy': data['step3']['potential_energy'],
                'volume': data['step3']['volume']/len(atoms),
                'B':B,
                'M':M}
    
    # save json data
    with open('atat.json','w') as f:
        f.write(json.dumps(jsondata))

    # print summary line
    print(s.format(**jsondata))
    return jsondata # in case this is ever called as a function
        
if __name__ == '__main__':
    # if we are in the queue, run the function above
    if 'PBS_O_WORKDIR' in os.environ:
        JASPRC['mode'] = 'run'  # so we can run in the queue
        try:
            run()
        except:
            open('error', 'w').close()
            
    else:
        # we are not in the queue, so we should submit a job if needed
        if os.path.exists('atat.json'):
            run() # this will print data and return
            sys.exit()
        # see if a job exists. Exit if it does.
        elif os.path.exists('jobid'):
            with open('jobid') as f:
                jobid = f.readline()
            print('jobid {0} exists.'.format(jobid))
            sys.exit()

        # now, submit a job
        script = '''
#!/bin/bash
cd $PBS_O_WORKDIR
python run_eosm.py
'''
        p = Popen(['qsub',
                   '-joe',
                   '-N',
                   "%s" % os.getcwd(),
                   '-l walltime=168:00:00'],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)

        out, err = p.communicate(script)
        f = open('jobid','w')
        f.write(out)
        f.close()
        print('|[[shell:qstat -f %s][%s]]|' % (out.strip(),out.strip()))
