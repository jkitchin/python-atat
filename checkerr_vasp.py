#!/usr/bin/env python
'''
Analyze vasp.out.* files from atat for errors.
'''

error_strings = ['forrtl: severe',  #seg-fault
                 'highest band is occupied at some k-points!',
                 # these are the things checkerr_vasp catches
                 'rrrr', # I think this is from Warning spelled out
                 'cnorm',
                 'failed',
                 'non-integer',]

warning_strings = ['warn']

def checkerr_file(of):
    '''check one file for errors

    I separate out this out because it returns from a nested loop,
    which makes it stop after the first error.
    '''
    f = open(of, 'r')
    for line in f:
        for es in error_strings:
            if es in line.lower():
                f.close()
                return '%s: %s' % (of,es)
    f.close()
    return None

def checkwarn_file(of):
    '''check one file for warnings

    I separate out this out because it returns from a nested loop,
    which makes it stop after the first warning.
    '''
    f = open(of, 'r')
    for line in f:
        for ws in warning_strings:
            if ws in line.lower():
                f.close()
                return '%s: %s' % (of,ws)
    f.close()
    return None

def checkerr_vasp():
    '''replacement for checkerr_vasp'''
    output_files = ['vasp.out',
                    'vasp.out.relax',
                    'vasp.out.static']

    warnings,errors = [],[]

    for of in output_files:
        err = checkerr_file(of)
        if err:
            errors.append(err)

        warn = checkwarn_file(of)
        if warn:
            warnings.append(warn)

    if len(errors) > 0:
        f = open('error', 'w')
        for es in errors:
            f.write(es + '\n')
        f.close()
    else:
        print 'No errors found'

    if len(warnings) > 0:
        f = open('warning', 'w')
        for ws in warnings:
            f.write(ws + '\n')
        f.close()
    else:
        print 'No warnings'


if __name__ == '__main__':
    checkerr_vasp()
