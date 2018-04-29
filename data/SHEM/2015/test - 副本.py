import os

for i in range(1, 26):
        fn = 'bsh%02d2015.dat' % i
        nfn = 'SH%02d.txt' % i
        os.rename(fn, nfn)
