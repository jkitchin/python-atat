from ase import Atom, Atoms
from numpy import array, dot, transpose
from string import split

def str2atoms(file='str.out'):
    '''
    The str.out file starts with 3 lines defining the coordinate system
    [ax]  [ay]  [az]
    [bx]  [by]  [bz]
    [cx]  [cy]  [cz]

    then there are 3 lines defining the lattice vectors in terms of the
    coordinate system:
    [ua]  [ub]  [uc]
    [va]  [vb]  [vc]
    [va]  [wb]  [wc]

    where the actual lattice vectors are given by dot([u,v,w],[a,b,c])
    I think this defines the unit cell

    then, the rest of the lines correspond to atom positions:
    [atom a] [atom b] [atom c]  [atomtype]

    where the position is given by dot([[atom a] [atom b] [atom c],[a,b,c]
    '''

    f = open(file,'r')

    lines = f.readlines()
    numlines = len(lines)

    # these are the cooridinate system vectors: A, B, C
    A = array([float(a) for a in split(lines[0])])
    B = array([float(a) for a in split(lines[1])])
    C = array([float(a) for a in split(lines[2])])

    GCS = array([A,B,C])

    # these are the lattice vectors: U, V, W
    # U = aA + bB + cC

    U = array([float(a) for a in split(lines[3])])
    V = array([float(a) for a in split(lines[4])])
    W = array([float(a) for a in split(lines[5])])

    unitcell = array([dot(transpose(GCS),U),
                      dot(transpose(GCS),V),
                      dot(transpose(GCS),W)])

    atoms = Atoms([], cell=unitcell)

    for n in range(6,numlines):
        # each line is [a,b,c] in terms of the global coordinates
        fields = split(lines[n])

        pos = array([float(a) for a in fields[0:3]])
        pos = dot(transpose(GCS),pos)

        position = pos
        type = fields[-1]

        atoms.append(Atom(type, pos, tag=1))

    f.close()

    #nmake sure all atoms are in the cell
    spos = atoms.get_scaled_positions()

    spos_wrapped = []
    for i, pos in enumerate(spos):
        pos = pos % [1, 1, 1]

        truth = abs(pos - 1) < 1e-4;
        if truth.any():
            pos[truth] = 0.0
        spos_wrapped.append(pos)

    atoms.set_scaled_positions(spos_wrapped)
    return atoms


def atoms2str(atoms,strout='str.out'):

    unitcell = atoms.get_cell()
    positions = atoms.get_positions()

    f = open(strout, 'w')
    f.write('1.0 0.0 0.0\n')
    f.write('0.0 1.0 0.0\n')
    f.write('0.0 0.0 1.0\n')
    f.write('%1.5f %1.5f %1.5f\n' % tuple(unitcell[0]))
    f.write('%1.5f %1.5f %1.5f\n' % tuple(unitcell[1]))
    f.write('%1.5f %1.5f %1.5f\n' % tuple(unitcell[2]))
    for atom in atoms:
        f.write('%1.5f %1.5f %1.5f %s\n' % tuple(tuple(atom.position)+(atom.symbol,)))

    f.close()
