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