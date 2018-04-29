import os

for i in range(21, 30):
        fn = 'bwp%02d2016.dat' % i
        nfn = 'WP%02d.txt' % i
        os.rename(fn, nfn)
