# pybst

Use pybst to navigate BST data.

```pycon
>>> import pybst
>>> cyclone = pybst.BST('haiyan')
3 storm(s) found.
1. 200125W
2. 200727W
3. 201331W
Select a storm:3

>>> cyclone.name
'HAIYAN'
>>> cyclone.num
'201331'
>>> cyclone.basin
'WP'
>>> cyclone.info()
Time            Lat     Lon     Wind    Pres    Status
2013/11/02 0600Z        6.6     161.6   15      1010    DB
2013/11/02 1200Z        6.2     160.3   15      1010    DB
2013/11/02 1800Z        6.1     158.8   15      1010    DB
...
2013/11/11 0600Z        23.2    107.9   45      989     TS

Name: HAIYAN
Birth: 2013/11/02 0600Z Death: 2013/11/11 0600Z
Peak Intensity: 170kt
Peak Time |  2013/11/07 1200Z |  2013/11/07 1800Z |
ACE: 38.1925
Movement Length: 6730.0km
>>> pybst.ace('201331')
38.1925
>>> pybst.jtwctojma('201331')
'201330J'
>>> pybst.stormname('201520E')
'PATRICIA'
>>> pybst.BST('patricia').peak()
5 storm(s) found.
1. 197016E
2. 197416E
3. 200316E
4. 200919E
5. 201520E
Select a storm:5

[[185, '201510231200', 17.3, -105.6, 872, 'HU', ' ']]
>>> pybst.currentstorm()
[['21S', 'FLAMBOYAN', '1804291200', -12.8, 86.3, 'SHEM', 60, 991], ['93W', 'INVEST', '1804281800', 4.4, 142.4, 'WPAC', 15, 1010], ['95W', 'INVEST', '1804291200', 8.1, 157.6, 'WPAC', 15, 1005]]
>>> pybst.yearace()
1970    0.0     21.21   0.0     0.0     0.0     6.0075  23.7775 78.7875 57.6875 73.36   26.6975 0.0 287.5275
1971    1.63    0.0     0.2025  18.58   53.36   14.1475 82.6325 69.64   84.6875 26.2375 28.3875 0.0 379.5050
1972    8.2525  0.0     0.0     0.0     3.335   21.93   141.935 57.035  48.525  75.01   36.9175 30.05   422.9900
...
2016    0.0     0.0     0.0     0.0     0.0     0.0     29.6225 49.8425 74.215  75.21   11.755  18.425  259.0700
2017    0.0     0.0     0.0     1.045   0.0     0.97    41.6575 43.4025 26.7325 33.4025 5.875   0.0 153.0850
>>> pybst.season_view(2017)
WP012017        NOTNAMED        30kt    1001hPa TD      01/08
WP022017        NOTNAMED        25kt    1005hPa TD      04/14
WP032017        MUIFA           40kt    1002hPa TS      04/26
...
WP302017        HAIKUI          40kt    1002hPa TS      11/10
WP312017        KIROGI          40kt    1000hPa TS      11/18
```
