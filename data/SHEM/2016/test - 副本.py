import os

for i in range(11, 26):
        fn = 'bsh%02d2016.dat' % i
        nfn = 'SH%02d.txt' % i
        os.rename(fn, nfn)
