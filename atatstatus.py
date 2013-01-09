#!/usr/bin/env python
'''
list the status of each structure directory in atat

check for existence of the error file, energy file and jobid file, and summarize the status in one line.

The output is in org-mode format, which has links when viewed in emacs.
'''

import commands, glob, os, sys

if len(sys.argv) == 1:
    dir = '.'
else:
    dir = sys.argv[1]
    os.chdir(dir)

directories = []

# find newest energy and error file
mtime = 0.0
energy_files = glob.glob('*/energy')
for ef in energy_files:
    this_mtime = os.path.getmtime(ef)
    if this_mtime > mtime:
        mtime = this_mtime

for ef in glob.glob('*/error'):
    this_mtime = os.path.getmtime(ef)
    if this_mtime > mtime:
        mtime = this_mtime

if not os.path.exists('maps.log'):
    print('It seems there is no maps.log yet.')
    import sys; sys.exit()

maps_mtime = os.path.getmtime('maps.log')
if maps_mtime > mtime:
    print '# maps.log is newer than all error/energy files. We are up to date.'
else:
    print '# newer energy or error files found. rerun maps -d.'


for d in os.listdir('.'):
    if os.path.isdir(d) and os.path.exists(d + '/str.out'):
        #we have a structure directory
        directories.append(d)

#intdirs = [int(x) for x in directories]
#intdirs.sort()
#directories = [str(x) for x in intdirs]

directories.sort()

lines = []
for d in directories:
    status = None
    if os.path.exists(d + '/error'):
        status = '      error'
    elif os.path.exists(d + '/energy'):
		f = open(d + '/energy')
	 	e1 = f.readline().strip()
	 	if e1 == '':
	 		status = ' empty energy'
	 	else:
	 		status = '  energy = % 1.4f' % (float(e1))
		f.close()
    elif os.path.exists(d + '/jobid'):
        f = open(d + '/jobid')
        jobid = f.readline().strip()
        f.close()

        if jobid == '':
            status = 'jobid is empty, resubmit'
        else:
            exitstatus, output = commands.getstatusoutput('qstat %s' % jobid)
            if exitstatus == 0:
                fields = output.split('\n')[2].split()
                queue_status = fields[4]
                status = '    {0} ({1})'.format(jobid,queue_status)
            else:
                status = '    jobid %s exists, but no job in queue' % jobid
    elif os.path.exists(d + '/wait'):
        status = '      waiting'

    # check for seg-fault errors
    for outfile in ['vasp.out','vasp.out.relax','vasp.out.static']:
        if os.path.exists(d + '/' +outfile):
            f = open(d + '/' + outfile)
            for line in f:
                if 'forrtl: severe' in line:
                    status = '  seg-fault'
                    g = open(d + '/error','w')
                    g.close()
                    break
                elif 'very serious problems' in line:
                    status = '  serious problems'
                    g = open(d + '/error','w')
                    g.close()
                    break
                elif 'Your highest band is occupied at some k-points!' in line:
                    status = '  highest band occupied'
                    g = open(d + '/error','w')
                    g.close()
                    break
            f.close()

    if status is None:
        status = '   Unknown'

    lines.append((d,status,d))

# Now we print the output in org-table format
# find max length of each column so we can create a format string
# that prints an aligned table.
c0 = [len(x[0]) for x in lines]
c1 = [len(x[1]) for x in lines]

m1 = max(c0)
m2 = max(c1)

f1 = '%%%is' % (m1+2)
f2 = '%%%ss' % (m2 + 2)

format_ = '|%s|%s|' % (f1,f2)
if len(lines) > 10:
    print '#+ATTR_LaTex: longtable'
print '#+tblname: atatstatus.py'
print '|configuration| status | command|'
print '|-'
for tup in lines:
    print (format_ + '[[ashell:xterm -e "cd %s; ls && /bin/bash"][xterm]]|') % tup
