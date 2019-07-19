'''Faster and easier as a stand-alone script than as part of the website.

This script will filter an iputtable as provided by MIT conference services
remove all non-pubic information (keeping name and institution of participants
who did not opt-out) and pass that into a simply text file
which can then we used in the website scripts and commited to the data
directory.
'''
from astropy.table import Table
t = Table.read('../Registrants_full.csv', format='ascii.csv')
t = t[t['Click here to opt out of a published registrant list.'].mask]

t['out'] = ['{} {} ({})'.format(row['First Name'], row['Last Name'], row['Company'] or 'Guest') for row in t]

t.sort(['Last Name', 'First Name'])
tout = t[['out']]
tout.write('data/reglist.csv', format='ascii.csv')
