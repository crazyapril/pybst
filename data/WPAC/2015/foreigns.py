for i in range(1,30):
    f = open('bwp%02d2015.dat' % (i), 'r')
    f2 = open('WP%02d.txt' % (i), 'w')
    f2.write(f.read())
    f.close()
    f2.close()
