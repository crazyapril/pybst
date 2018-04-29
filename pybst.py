import datetime as dt
import math
import os
from urllib.request import urlopen, urlretrieve

import numpy as np

__CWD__ = os.path.dirname(os.path.abspath(__file__))
__BSTDIR__ = os.path.join(__CWD__, 'data')
__NAMEDIR__ = os.path.join(__CWD__, 'namebase')
__ACEDIR__ = os.path.join(__CWD__, 'ace')
__NRLSECTOR__ = 'http://tropic.ssec.wisc.edu/real-time/amsu/herndon/new_sector_file'

def numcode(code):
    if not code[0].isdigit():
        return namecode(code)
    if code[-1].isdigit():
        code = code + 'W'
    if len(code) != 7:
        return 'unknown', 'unknown', -1, code
    basincode = code[-1]
    if basincode == 'E':
        return 'EP', 'hursat', 0, code[:-1]
    elif basincode == 'C':
        return 'CP', 'hursat', 0, code[:-1]
    elif basincode == 'I':
        return 'IO', 'bdeck', 0, code[:-1]
    elif basincode == 'J':
        return 'WP', 'jma', 0, code[:-1]
    elif basincode == 'L':
        return 'AL', 'hursat', 0, code[:-1]
    elif basincode == 'S':
        return 'SH', 'bdeck', 0, code[:-1]
    elif basincode == 'W':
        return 'WP', 'bdeck', 0, code[:-1]
    elif basincode == '*':
        return 'PR', 'bdeck', 0, code[:-1]
    else:
        return 'unknown', 'unknown', -1, code

def BST(code):
    basin, form, yr, num = numcode(code)
    if yr == 1:
        return 1
    elif yr != 0:
        return 0
    try:
        if form == 'bdeck':
            return BDECK(num, basin)
        elif form == 'hursat':
            return HURSAT(num, basin)
        elif form == 'jma':
            return JMA(num)
    except IOError:
        return 0

def stormname(code):
    basin, form, yr, num = numcode(code)
    assert yr == 0
    if basin == 'WP':
        if int(num[:-2]) < 1970:
            return 'WP%s%s' % (num[-2:], num[:-2])
        else:
            f = open(os.path.join(__NAMEDIR__, 'namebase.txt'),'r')
            line = f.readline()
            while line:
                if line[:6] == num:
                    f.close()
                    return line[14:-1]
                line = f.readline()
            f.close()
            return 'unknown'
    elif basin == 'AL' or basin == 'EP' or basin == 'CP':
        if basin == 'AL':
            f = open(os.path.join(__NAMEDIR__, 'Lnamebase.txt'),'r')
        else:
            f = open(os.path.join(__NAMEDIR__, '%snamebase.txt' % (basin[0])),'r')
        line = f.readline()
        while line:
            if line[:6] == num:
                f.close()
                return line[7:-1]
            line = f.readline()
        f.close()
        return 'unknown'

def hursatname(basin, num, handle=False):
    if basin == 'AL':
        earliest, filebasin = 1845, 'ATL'
    else:
        earliest, filebasin = 1949, 'EPAC'
    if int(num[:-2]) < earliest:
        return '%s%s%s' % (basin, num[-2:], num[:-2])
    else:
        f = open(os.path.join(__BSTDIR__, '%s\hursat.txt' % (filebasin)),'r')
        atcfnum = '%s%s%s' % (basin, num[-2:], num[:-2])
        line = f.readline()
        while line:
            if line[:8] == atcfnum:
                if handle:
                    return line[18:28].strip(), f, f.tell()
                else:
                    f.close()
                    return line[18:28].strip()
            else:
                rows = int(line[33:36])
                for i in range(rows):
                    f.readline()
                line = f.readline()
        f.close()
        if handle:
            return 'unknown', 0, 0
        else:
            return 'unknown'

def namecode(name):
    if len(name) < 2:
        return 'unknown','unknown',-1,name
    name = name.upper()
    basinshort = ['W', 'L', 'E', 'C']
    basinlist = ['WP', 'AL', 'EP', 'CP']
    if name[-2] == '#' and name[-1] in basinshort:
        stormlist = namesearcher(name[:-2],basin=basinlist[basinshort.index(name[-1])])
    else:
        stormlist = namesearcher(name)
    listlen = len(stormlist)
    if listlen == 0:
        print('Storm \'%s\' not found.' % (name))
        return 'unknown','unknown',-1,name
    else:
        print('%d storm(s) found.' % (listlen))
        for i in range(listlen):
            print('%d. %s' % (i+1, stormlist[i]))
        if listlen == 1:
            if stormlist[0][-1] == 'W':
                fmt = 'bdeck'
            else:
                fmt = 'hursat'
            print()
            return basinlist[basinshort.index(stormlist[0][-1])], fmt, 0, stormlist[0][:-1]
        else:
            choice = 0
            while choice not in list(range(1, listlen+1)):
                choice = eval(input('Select a storm:'))
            if stormlist[choice-1][-1] == 'W':
                fmt = 'bdeck'
            else:
                fmt = 'hursat'
            print()
            return basinlist[basinshort.index(stormlist[choice-1][-1])], fmt, 0, stormlist[choice-1][:-1]
        
def namesearcher(name, basin='all'):
    stormlist = []
    name = name.upper()
    if name == 'NOTNAMED' or name == 'UNNAMED':
        return stormlist
    if basin == 'WP' or basin == 'all':
        f_wp = open(os.path.join(__NAMEDIR__, 'namebase.txt'),'r')
        line = f_wp.readline()
        while line:
            if line[14:-1].strip() == name and line[0].isdigit():
                stormlist.append(line[:6]+'W')
            line = f_wp.readline()
        f_wp.close()
    if basin == 'AL' or basin == 'all':
        f_al = open(os.path.join(__NAMEDIR__, 'Lnamebase.txt'),'r')
        line = f_al.readline()
        while line:
            if line[7:-1] == name:
                stormlist.append(line[:6]+'L')
            line = f_al.readline()
        f_al.close()
    if basin == 'EP' or basin == 'all':
        f_ep = open(os.path.join(__NAMEDIR__, 'Enamebase.txt'),'r')
        line = f_ep.readline()
        while line:
            if line[7:-1] == name:
                stormlist.append(line[:6]+'E')
            line = f_ep.readline()
        f_ep.close()
    if basin == 'CP' or basin == 'all':
        f_cp = open(os.path.join(__NAMEDIR__, 'Cnamebase.txt'),'r')
        line = f_cp.readline()
        while line:
            if line[7:-1] == name:
                stormlist.append(line[:6]+'C')
            line = f_cp.readline()
        f_cp.close()
    return stormlist

def ace(code):
    one = BST(code)
    if one == 0:
        return -1
    windlist = one.datalist(tropical=True)[3]
    del one
    return acecal(windlist)

def acecal(windlist):
    ace = 0
    for num in windlist:
        if num >= 35 and num < 300:
            ace += num * num
    return ace/10000.0

def jtwctojma(code):
    basin, form, yr, num = numcode(code)
    assert yr == 0 and basin == 'WP'
    f = open(os.path.join(__NAMEDIR__, 'namebase.txt'),'r')
    line = f.readline()
    if form == 'bdeck':    #mode=0,jtwc to jma; others, jma to jtwc
        fro, to = 0, 6
        rfro, rto = 7, 13
    else:
        fro, to = 7, 13
        rfro, rto = 0, 6
    while line:
        if line[fro:to] == num:
            f.close()
            if form == 'bdeck':
                return line[rfro:rto] + 'J'
            else:
                if line[0].isdigit():
                    return line[rfro:rto] + 'W'
                elif line[1] == '0':
                    return '2' + line[rfro+1:rto] + line[0]
                elif line[1] == '9':
                    return '1' + line[rfro+1:rto] + line[0]
        line = f.readline()
    f.close()
    return ''

def length(code):
    one = BST(code)
    if one == 0:
        return -1
    datalist = one.datalist()
    windlist, latlist, lonlist = datalist[3], datalist[1], datalist[2]
    del one
    return lengthcal(latlist, lonlist)

def lengthcal(latlist, lonlist):
    arc = 0
    for i in range(len(latlist)-1):
        lat, lon = latlist[i], lonlist[i]
        plat, plon = latlist[i+1], lonlist[i+1]
        dtr = math.pi/180.0
        phi1 = (90.0 - lat) * dtr
        phi2 = (90.0 - plat) * dtr
        theta1 = lon * dtr
        theta2 = plon * dtr
        cosv = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
        if cosv > 1:
            cosv = 1
        arc += math.acos(cosv)
    return arc * 6373.0

def sshws(wind):
    if wind > 300:
        cat = 'unknown'
    elif wind > 137:
        cat = 'C5'
    elif wind > 114:
        cat = 'C4'
    elif wind > 96:
        cat = 'C3'
    elif wind > 83:
        cat = 'C2'
    elif wind > 64:
        cat = 'C1'
    elif wind > 30:
        cat = 'TS'
    else:
        cat = 'TD'
    return cat

def wikicolor(wind):
    cat = sshws(wind)
    wikicolors = {'unknown':'grey', 'C5':'#ff5e5e', 'C4':'#ff8f1d',
                  'C3':'#ffbe49', 'C2':'#ffe473', 'C1':'#ffffc7', 'TS':'#03f8f9', 'TD':'#59bbff'}
    return wikicolors[cat]

def wikicolormap():
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap(['#59bbff', '#03f8f9', '#ffffc7', '#ffe473', '#ffbe49', '#ff8f1d', '#ff5e5e'])
    norm = BoundaryNorm([5, 30, 64, 83, 96, 114, 137, 200], cmap.N)
    return cmap, norm

def wikicolorlegend(labels=['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5']):
    from matplotlib.patches import Patch
    wikicolors = ['#59bbff', '#03f8f9', '#ffffc7', '#ffe473', '#ffbe49', '#ff8f1d', '#ff5e5e']
    handles = []
    for l, w in zip(labels, wikicolors):
        handles.append(Patch(color=w, label=l))
    return handles

def dtime(time):
    return '%s/%s/%s %sZ' % (time[:4], time[4:6], time[6:8], time[8:12])

def kzc(msw, motion, ap, lat, r):
    relative_intensity = msw - 1.5 * motion ** 0.63
    tmpval1 = 66.785 - 0.09102 * msw + 1.0619 * (lat - 25)
    tmpval2 = 0.1147 + 0.0055 * msw - 0.0001 * (lat - 25)
    climatological_size = msw * (tmpval1 / 500) ** tmpval2
    tropical_cyclone_size = r / 9 - 3
    size_factor = tropical_cyclone_size / climatological_size
    if size_factor <= 0.4:
        size_factor = 0.4
    if lat < 18:
        delta_p = 5.962 - 0.267 * relative_intensity - (relative_intensity / 18.26) ** 2 -\
                  6.8 * size_factor
    else:
        delta_p = 23.286 - 0.483 * relative_intensity - (relative_intensity / 24.254) ** 2 -\
                  12.587 * size_factor - 0.483 * lat
    return ap - delta_p

def foreigns(yr):
    yr = str(yr)
    if not yr.isdigit():
        return
    try:
        f = open(os.path.join(__BSTDIR__, 'WPAC/%s/foreigns.txt' % (yr)), 'r')
    except IOError:
        return []
    tclist = []
    line = f.readline()
    while line:
        tclist.append(line[:-1])
        line = f.readline()
    f.close()
    return tclist

def shiftlons(arr):
    arr = np.array(arr)
    arr[arr < 0] = 360 + arr[arr < 0]
    return arr

class BDECK:
    def __init__(self, code, basin):
        self.num = code
        self.basin = basin
        if basin == 'PR':
            self.f = open(os.path.join(__BSTDIR__, r'WPAC\%sPRE\WP%s.txt' % (code[0:4], code[4:6])),'r')
        else:
            basindict = {'WP':'WPAC', 'SH':'SHEM', 'IO':'NIO'}
            self.f = open(os.path.join(__BSTDIR__, r'%s\%s\%s%s.txt' % (basindict[basin], code[0:4], basin, code[4:6])),'r')
        self.name = stormname(code)
        self.time, self.wind, self.lat, self.lon, self.pres, self.level = '0', 0, 0.0, 0.0, 0, ''
        self.eyed = 0

    def readline(self):
        line = self.f.readline()
        if line:
            self.time = '%s00' % (line[8:18])
            self.wind = int(line[48:51])
            if self.wind > 300:
                self.wind = -1
            self.lat, self.lon = self.position(line)
            if line[53:57] == '':
                self.pres = 0
            else:
                self.pres = int(line[53:57])
            self.level = line[59:61]
            if line[119:122] == '':
                self.eyed = 0
            else:
                self.eyed = int(line[119:122])
        else:
            self.time, self.wind, self.lat, self.lon, self.pres, self.level,self.eyed = '', 0, 0.0, 0.0, 0, '',0

    def position(self, line):
        lat = int(line[35:38]) / 10.0
        lon = int(line[41:45]) / 10.0
        if line[38] == 'S':
            lat = -lat
        if line[45] == 'W':
            lon = -lon
        return lat, lon

    def windline(self):
        pasttime = self.time
        while self.time == pasttime and self.time != '':
            self.readline()
        return self.wind

    def datalist(self, tropical=False, allow_not_round=False):
        line = self.f.readline()
        pasttime = ''
        windlist = []
        latlist, lonlist = [], []
        timelist, levellist = [], []
        while line:
            nowtime = line[8:18]
            if nowtime != pasttime and (allow_not_round or nowtime[-2:] in ['00', '06', '12', '18']):
                if not (tropical and line[59:61] in ['EX', 'SS', 'SD']):
                    timelist.append('%s00' % (line[8:18]))
                    if int(line[48:51]) < 300:
                        windlist.append(int(line[48:51]))
                    else:
                        windlist.append(0)
                    lat, lon = self.position(line)
                    latlist.append(lat)
                    lonlist.append(lon)
                    levellist.append(line[59:61])
            pasttime = nowtime
            line = self.f.readline()
        return [timelist, latlist, lonlist, windlist, levellist]

    def get_datalist(self, tropical=False, allow_no_round=False):
        datalist_condition = tropical, allow_no_round
        if hasattr(self, 'datalist_cache') and datalist_condition == self.dlcond:
            return self.datalist_cache
        self.dlcond = datalist_condition
        self.datalist_cache = self.datalist(tropical=tropical, allow_not_round=allow_no_round)
        return self.datalist_cache

    def windmax(self):
        windlist = self.get_datalist()[3]
        if len(windlist) == 0:
            return 0
        else:
            return max(windlist)

    @property
    def time_as_ts(self):
        dllist = self.get_datalist()
        for i, w in enumerate(dllist[3]):
            if w >= 35:
                return dt.datetime.strptime(dllist[0][i], '%Y%m%d%H')

    def refresh(self):
        self.f.seek(0,0)
        self.time, self.wind, self.lat, self.lon, self.pres, self.level = '0', 0, 0.0, 0.0, 0, ''
        self.eyed = 0

    def peak(self):
        windmax, peakdetail = 0, []
        wind = self.windline()
        while wind:
            if wind > windmax:
                peakdetail = [[self.wind, self.time, self.lat, self.lon, self.pres, self.level]]
                windmax = wind
            elif wind == windmax:
                peakdetail.append([self.wind, self.time, self.lat, self.lon, self.pres, self.level])
            wind = self.windline()
        return peakdetail

    def info(self):
        print('Time\t\tLat\tLon\tWind\tPres\tStatus')
        pasttime = 'Null'
        self.readline()
        while self.wind != 0:
            if pasttime == self.time:
                self.readline()
                continue
            if self.level == 'TY' or self.level == 'ST':
                status = self.level + '/' + sshws(self.wind)
            elif self.level == '':
                status = sshws(self.wind)
                if self.wind >= 130:
                    status = 'ST/' + status
                elif self.wind >= 65:
                    status = 'TY/' + status
            else:
                status = self.level
            print('%s\t%.1f\t%.1f\t%d\t%d\t%s' % (dtime(self.time), self.lat, self.lon, self.wind, self.pres, status))
            pasttime = self.time
            self.readline()
        print('\nName: %s' % (self.name))
        self.refresh()
        dlist = self.get_datalist()
        print('Birth: %s Death: %s' % (dtime(dlist[0][0]), dtime(dlist[0][-1])))
        print('Peak Intensity: %dkt' % (max(dlist[3])))
        print('Peak Time | ', end=' ')
        self.refresh()
        peak = self.peak()
        for pk in peak:
            print('%s | ' % (dtime(pk[1])), end=' ')
        print()
        self.refresh()
        dlist2 = self.get_datalist(tropical=True)
        print('ACE: %.4f' % (acecal(dlist2[3])))
        print('Movement Length: %.1fkm' % (lengthcal(dlist[1], dlist[2])))
    
    def __del__(self):
        if hasattr(self, 'f'):
            self.f.close()

class HURSAT:
    def __init__(self, num, basin):
        self.num = num
        self.atcfnum = basin + num[4:] + num[:4]
        self.basin = basin
        self.name, self.f, self.ftell = hursatname(basin, num, handle=True)
        if self.f == 0:
            raise IOError
        self.time, self.wind, self.lat, self.lon, self.pres, self.level, self.event = '', 0, 0.0, 0.0, 0, '', ''

    def readline(self):
        #print self.f.tell()
        line = self.f.readline()
        #print self.f.tell()
        #print line
        if line == '':
            self.time, self.wind, self.lat, self.lon, self.pres, self.level, self.event = '', 0, 0.0, 0.0, 0, '', ''
        elif line[0] == '1' or line[0] == '2':
            self.time = '%s%s' % (line[0:8], line[10:14])
            self.event = line[16]
            self.level = line[19:21]
            self.lat, self.lon = self.position(line)
            self.wind = int(line[38:41])
            self.pres = int(line[43:47])
        else:
            self.time, self.wind, self.lat, self.lon, self.pres, self.level, self.event = '', 0, 0.0, 0.0, 0, '', ''

    def position(self, line):
        lat = eval(line[23:27])
        lon = eval(line[30:35])
        if line[27] == 'S':
            lat = -lat
        if line[35] == 'W':
            lon = -lon
        return lat, lon

    def windline(self):
        self.readline()
        return self.wind

    def datalist(self, event=False, tropical=False):
        '''return [time, lat, lon, wind, pres]'''
        self.readline()
        timelist, latlist, lonlist, windlist, preslist = [], [], [], [], []
        while self.wind:
            if event or self.time[-4:-2] in ['00', '06', '12', '18']:
                if not (tropical and self.level in ['EX', 'SS', 'SD', 'LO']):
                    timelist.append(self.time)
                    latlist.append(self.lat)
                    lonlist.append(self.lon)
                    windlist.append(self.wind)
                    preslist.append(self.pres)
            self.readline()
        return [timelist, latlist, lonlist, windlist, preslist]

    def windmax(self, pres=False):
        if pres:
            datalist = self.datalist(event=True)
            windlist, preslist = datalist[3], datalist[4]
            return max(windlist), min(preslist)
        else:
            windlist = self.datalist(event=True)[3]
            return max(windlist)

    def peak(self):
        windmax, presmin, peakdetail = 0, 1050, []
        wind = self.windline()
        while wind:
            if wind > windmax:
                peakdetail = [[self.wind, self.time, self.lat, self.lon, self.pres, self.level, self.event]]
                windmax = wind
            elif wind == windmax:
                peakdetail.append([self.wind, self.time, self.lat, self.lon, self.pres, self.level, self.event])
            wind = self.windline()
        return peakdetail

    def recordid(self, record):
        if record == ' ':
            return ' '
        elif record == 'L':
            return 'Landfall'
        elif record == 'W':
            return 'Max Wind'
        elif record == 'P':
            return 'Min Pres'
        elif record == 'I':
            return 'Peak'
        elif record == 'C':
            return 'Closest to Coast'
        elif record == 'S':
            return 'Status Change'
        elif record == 'G':
            return 'Genesis'
        elif record == 'T':
            return 'Additional Detail'
        else:
            return record

    def info(self):
        print('Time\t\tLat\tLon\tWind\tPres\tStatus\tRecord')
        wind = self.windline()
        windmax, presmin = 0, 1050
        windpeak, prespeak = [], []
        while wind:
            if self.event == ' ':
                event = ' '
            else:
                event = self.recordid(self.event)
            if self.level == 'HU' or self.level == 'TY':
                level = self.level + '/' + sshws(self.wind)
            else:
                level = self.level
            print('%s\t%.1f\t%.1f\t%d\t%d\t%s\t%s' % (dtime(self.time), self.lat, self.lon, self.wind, self.pres, level, event))
            if self.wind > windmax:
                windmax = self.wind
                windpeak = [self.time]
            elif self.wind == windmax:
                windpeak.append(self.time)
            if self.pres < presmin and self.pres > 0:
                presmin = self.pres
                prespeak = [self.time]
            elif self.pres == presmin:
                prespeak.append(self.time)
            wind = self.windline()
        print()
        self.refresh()
        print('Name: %s ATCF: %s' % (self.name, self.atcfnum))
        datalist = self.datalist()
        adv = len(datalist[0])
        print('Birth: %s Death: %s Lifetime: %dh (%d advisories)' % (dtime(datalist[0][0]), dtime(datalist[0][-1]), adv * 6 - 6, adv))
        print('Peak intensity: %dkt %dhPa' % (windmax, presmin))
        print('Max Wind Time', end=' ')
        for time in windpeak:
            print(' | %s' % (dtime(time)), end=' ')
        print('\nMin Pres Time', end=' ')
        for time in prespeak:
            print(' | %s' % (dtime(time)), end=' ')
        print('\nACE: %.4f' % (acecal(datalist[3])))
        print('Movement Length: %.1fkm' % (lengthcal(datalist[1], datalist[2])))

    def refresh(self):
        if self.atcfnum[0] == 'A':
            self.f.seek(self.ftell, 0)
        else:
            print(self.atcfnum, self.ftell)
            self.f.seek(self.ftell, 0)

    def __del__(self):
        if self.f != 0:
            self.f.close()

def currentstorm():
    url = __NRLSECTOR__
    sectors = urlopen(url)
    cstorms = []
    line = sectors.readline().decode(encoding='ascii')
    while line:
        sstorm = []
        data = line.split()
        sstorm.append(data[0]) #ATCFNUM
        sstorm.append(data[1]) #NAME
        sstorm.append(data[2]+data[3]) #TIME
        lat, lon = eval(data[4][:-1]), eval(data[5][:-1])
        if data[4][-1] == 'S':
            lat = -lat
        if data[5][-1] == 'W':
            lon = 360-lon
        sstorm.append(lat) #LATITUDE
        sstorm.append(lon) #LONGTITUDE
        sstorm.append(data[6]) #BASIN
        sstorm.append(int(data[7])) #WIND
        sstorm.append(int(data[8])) #PRESSURE
        line = sectors.readline().decode(encoding='ascii')
        cstorms.append(sstorm)
    sectors.close()
    return cstorms

def dailyace(year='mean', date=(12,31), datelist=False, basin='WPAC'):
    year = str(year)
    if year in ['mean', 'max', 'min'] + ['%d' % (i) for i in range(1970,2050)]:
        fname = os.path.join(__ACEDIR__, '%s\%s.txt' % (basin, year))
    else:
        return []
    if date == (0,0):
        date = (dt.date.today().timetuple().tm_mon, dt.date.today().timetuple().tm_mday)
    acevalues = np.genfromtxt(fname,delimiter='\t',skip_header=2,dtype=float)
    yday = dt.date(2013, date[0], date[1]).timetuple().tm_yday
    if datelist:
        return acevalues[:yday], [dt.datetime.strptime('%d' % (i+1), '%j') for i in range(yday)]
    else:
        return acevalues[:yday]

def yearace(yr=None, date=None, basin='WPAC'):
    if yr:
        if not date:
            date = (dt.date.today().timetuple().tm_mon, dt.date.today().timetuple().tm_mday)
        data, dates = dailyace(yr, date, True)
        print(yr)
        i = 0
        for value, date in zip(data, dates):
            print('%s\t%.4f' % (date.strftime('%m/%d'), value), end='\t')
            i += 1
            if i % 4 == 0:
                print()
        print()
    else:
        thisyear = dt.datetime.today().year
        for year in range(1970, thisyear+1):
            fname = os.path.join(__ACEDIR__, '%s\%s.txt' % (basin, year))
            f = open(fname, 'r')
            acesum = f.readline()
            line = f.readline().split()
            print(year, end='\t')
            for i in range(12):
                print(eval(line[i]), end='\t')
            print(acesum[:-1])
            f.close()

def acesingle(yr, one, basin):
    print(one.name)
    flag = True if yr % 4 == 0 else False
    aceyear = np.zeros(365,dtype=np.float)
    data = one.datalist(tropical=True)
    for i in range(len(data[0])):
        time, lon, wind = data[0][i], data[2][i], data[3][i]
        if int(time[:4]) == yr and loninbasin(lon, basin) and wind > 30:
            yday = dt.datetime.strptime(time,'%Y%m%d%H%M').timetuple().tm_yday
            if flag and yday >= 60:
                yday -= 1
            aceyear[yday-1] += wind * wind / 10000.0
    return aceyear

def loninbasin(lon, basin):
    if basin == 'WPAC':
        return lon > 100
    elif basin == 'EPAC':
        return lon < -60
    elif basin == 'ATL':
        return True

def acerefresh(yr, basin='WPAC', refnum=None, refyr=None):
    '''acerefresh calculates ACE values of a year.
    Usage: acerefresh(2017, refnum=[10]) download 10W track file and calculate ACE values
    acerefresh(2016) recalculate ACE values of last year
    acerefresh('max') calculate max ACE values by date from 1970 through this year
    acerefresh('max', refyr=2016) calculate max ACE values by date from 1970 through 2016'''
    if yr in ['max', 'mean', 'min']:
        if refyr:
            yrnum = refyr - 1970 + 1
        else:
            yrnum = dt.date.today().year - 1970 + 1
        data = np.zeros((yrnum, 365))
        for yrs in range(yrnum):
            data[yrs, :] = dailyace(1970+yrs)
        if yr == 'max':
            newdata = np.amax(data, axis=0)
        elif yr == 'mean':
            newdata = np.mean(data, axis=0)
        elif yr == 'min':
            newdata = np.amin(data, axis=0)
        acewrite(yr, newdata)
        return
    flag = True if yr % 4 == 0 else False
    if basin == 'WPAC' and refnum != None:
        for rnum in refnum:
            bdeckdown('bwp%02d%d' % (rnum, yr))
    basincodedict = {'WPAC':'', 'EPAC':'E', 'ATL':'L'}
    basincode = basincodedict[basin]
    aceyear = np.zeros(365,dtype=np.float)
    num = 1
    while True:
        one = BST('%d%02d' % (yr, num) + basincode)
        if one == 0:
            break
        aceyear += acesingle(yr, one, basin)
        num += 1
    num = 1
    while True:
        one = BST('%d%02d' % (yr-1, num) + basincode)
        if one == 0:
            break
        num += 1
    one = BST('%d%02d' % (yr-1, num-1) + basincode)
    aceyear += acesingle(yr, one, basin)
    if basin == 'WPAC':
        try:
            foreigner = open(os.path.join(__BSTDIR__, 'WPAC/%d/foreigns.txt' % (yr)), 'r')
            code = foreigner.readline()
            while code:
                aceyear += acesingle(yr, BST(code[:-1]), basin)
                code = foreigner.readline()
        except IOError:
            pass
    elif basin == 'EPAC':
        num = 1
        while True:
            one = BST('%d%02dC' % (yr, num))
            if one == 0:
                break
            aceyear += acesingle(yr, one, basin)
            num += 1
    aceaccu = np.cumsum(aceyear)
    acewrite(yr, aceaccu, basin)

def acewrite(yr, aceaccu, basin='WPAC'):
    if yr in ['max', 'mean', 'min']:
        txt = open(os.path.join(__ACEDIR__, '%s/%s.txt' % (basin, yr)), 'w')
    else:
        txt = open(os.path.join(__ACEDIR__, '%s/%d.txt' % (basin, yr)), 'w')
    txt.write('%08.4f\n' % (aceaccu[-1]))
    for i in range(12):
        if i == 0:
            prevace = 0.
        else:
            prevace = aceaccu[dt.date(2009, i + 1, 1).timetuple().tm_yday - 2]
        if i == 11:
            nowace = aceaccu[-1]
        else:
            nowace = aceaccu[dt.date(2009, i + 2, 1).timetuple().tm_yday - 2]
        txt.write('%08.4f' % (nowace-prevace))
        txt.write('\t')
    txt.write('\n')
    for i in range(len(aceaccu)):
        txt.write('%08.4f\t' % (aceaccu[i]))
    txt.close()
    
def bdeckdown(code):
    if code[:3] != 'bwp':
        return 0
    url = 'http://ftp.emc.ncep.noaa.gov/wd20vxt/hwrf-init/decks/%s.dat' % (code)
    fname = os.path.join(__BSTDIR__, 'WPAC\%s\WP%s.txt' % (code[-4:], code[3:5]))
    urlretrieve(url, fname)
    return fname

def season(year, basin='W'):
    i = 1
    while True:
        storm_num = '{:d}{:02d}{:s}'.format(year, i, basin)
        one = BST(storm_num)
        if one == 0:
            break
        yield one
        i += 1

def season_view(year, basin='W'):
    for storm in season(year, basin):
        peaks = storm.peak()
        if len(peaks[0]) == 6:
            wind, time, lat, lon, pres, level = tuple(peaks[0])
        else:
            wind, time, lat, lon, pres, level, event = tuple(peaks[0])
        print('{}{}{}\t{:<12s}\t{}kt\t{}hPa\t{}\t{}/{}'.format(storm.basin, storm.num[-2:],
              storm.num[:4], storm.name, wind, pres, sshws(wind), time[4:6], time[6:8]))
