import json
from datetime import datetime
import numpy as np
import csv
from astropy.table import Table, Column, join

dates = {'': [2019, 8, 28],  # Posters don't have a date. They should be displayed last.
         'TBA': [2019, 7, 28],
         'Sun': [2019, 7, 21],
         'Mon': [2019, 7, 22],
         'Tue': [2019, 7, 23],
         'Wed': [2019, 7, 24],
         'Thu': [2019, 7, 25],
         'Fri': [2019, 7, 26],
         'Sat': [2019, 7, 27]}
'''Mapping between 3-character day code and date'''


def parse_day_time(day, timestr, end=False):
    '''Turn day and time string into a datetime object.

    If time is empty or "TBA", the return time is late in the
    afternoon to that not yet assigned talks get printed last
    in the list of sorted talks. A default for ``day`` can be set
    by adding the appropriate values to the look-up table ``dates``.

    Parameters
    ----------
    day : string
        index for lookup in ``dates`` table
    timestr : string
        string for time in the form "14:30 - 15:15".
    end : bool
        Return end time of event (default is start time)

    Returns
    -------
    datetime : `datetime.datetime`
        Start time of event as `datetime.datetime` object.
    '''
    if ((day is np.ma.masked) or (timestr is np.ma.masked) or (day is None)
        or (timestr is None)):
        return None
    i = 1 if end else 0
    if timestr in ['', 'TBA']:
        time = ['19', '00']
    else:
        time = timestr.split('-')[i].split(':')
    d = dates[day[:3]]
    return datetime(d[0], d[1], d[2], int(time[0].strip()), int(time[1].strip()))

contribtype = {'': 'not assigned',
               'poster': 'poster',
               'invited': 'invited review',
               'contributed': 'contributed talk'}


def combine_affils(affils):
    if len(affils) == 1:
        return affils[0]
    else:
        return '; '.join(affils)


def loctime(row):
    if row['type'] == 'poster':
        return 'poster number: {}'.format(row['poster number'])
    elif (row['type'] == 'invited') or (row['type'] == 'contributed'):
        if ('day' in row.colnames) and (row['day'] != ''):
            d = row['day']
        else:
            d = 'TBA'
        if ('time' in row.colnames) and (row['time'] != ''):
            t = row['time']
        else:
            t = 'time to be announced'
        return '{}, {}'.format(d, t)
    else:
        return ''

# missing in list below: mark invited talks
def write_json_abstracts(abstr):
    data = {'data': []}
    for row in abstr:
        data['data'].append({'type': contribtype[row['type']],
                             #'author': row['First author'],
                             #'authorlist': row['Authors'],
                             #'affiliations': row['affiliations'],
                             'author': 'anonymous',
                             'authorlist': 'anonymous',
                             'affiliations': 'anonymous',

                             'abstract': '<p class="abstract">' + row['Abstract'].replace('\n\n', '</p><p class="abstract">') + '</p>',
                             'title': row['Title of presentation'],
                             #'authoremail': "<a href='mailto:{0}'>{0}</a>".format(row['Email Address']) if row['Publish first author contact information?'] else '--',
                             #'link': '<a href="{0}">{0}</a>'.format(row['Link to electronic material']) if row['Link to electronic material'] else '--',
                             #'loctime': loctime(row),
                             #'index': row['index'],
                             'authoremail': '--',
                             'link': '--',
                             'loctime': loctime(row),
                             'index': row['index'],
                             'idnum': row['idnum']
                             })
    with open('data/abstracts.json', 'w') as fp:
        json.dump(data, fp)


def process_google_form_value(tab, **kwargs):
    '''Process the values collected in the Google abstract form

    Some of the form fields require some processing to get them into
    the forms that are most useful in building the abstract booklet
    and website, for example, the authorlist needs to be broken from a
    single long string into t list of strings.

    This function add new colums to a table ``tab``.
    '''
    tab['authorlist'] = [r.split('\n') for r in tab['Authorlist']]
    tab['First author'] = [r[0].split('(')[0].strip() for r in tab['authorlist']]
    tab['affiliations'] = [r.split('\n') for r in tab['Affiliations']]
    tab['affiliations'] = [combine_affils(r) for r in tab['affiliations']]
    tab['binary_time'] = [parse_day_time(r['day'], r['time']) for r in tab]
    tab['typepreference'] = [n.split(' ')[0] for n in tab['Presentation type']]

    team = Column(length=len(tab), dtype='<U140')
    for i, f in enumerate(tab['First author']):
        if " for " in f:
            a, b = f.split(' for ')
            tab['First author'][i] = a
            team[i] = ' for ' + b
    tab['team'] = team
    for i, t in enumerate(tab['team']):
        if t != '':
            tab['authorlist'][i][0] = tab['authorlist'][i][0].split(' for ')[0] + ' (1)'
            tab['affiliations'][i] = '(1) ' + tab['affiliations'][i]

    # Poster submissions will always be accepted as poster unless specifically
    # marked otherwise
    # Want to edit col, but might be too small to fit the string,
    # so make new col first
    newtype = Column(tab['typepreference'], dtype='<U20')
    if kwargs['autoacceptposters']:
        newtype[(newtype == '') & (tab['typepreference'] == 'poster')] = 'poster'
        tab['type'] = newtype

    # Now some checks
    ind_poster = tab['type'] == 'poster'
    posters = tab[ind_poster]

    # check it's a number otherwise sort will fail because string sorting will
    # give different answers
    if not np.issubdtype(posters['poster number'].dtype, np.integer):
        print('Poster numbers are not integers - they might be sorted randomly.')
    # check that no two posters have the same number
    unique_numbers, unique_counts = np.unique(posters['poster number'],
                                              return_counts=True)
    if (unique_counts > 1).sum() > 0:
        print('The following poster numbers are used more than once:')
        for i in (unique_counts > 1).nonzero()[0]:
            print('{}  is assigned to {} posters'.format(unique_numbers[i],
                                                         unique_counts[i]))


def read_abstracts_table(filename, **kwargs):
    out = []
    with open(filename, newline='') as f:
         reader = csv.reader(f)
         for row in reader:
             out.append(row)
    abstr = Table(rows=out[1:], names=out[0])
    abstr = abstr[abstr['Timestamp'] != '']
    process_google_form_value(abstr, **kwargs)
    return abstr


def data(**kwargs):
    if kwargs['abstracts'] is None:
        write_json_abstracts([])
        return {'talks': [], 'posters': [], 'unassigned': []}
    # abstr = Table.read(abstrfile, fast_reader=False, fill_values=())
    abstr = read_abstracts_table(kwargs['abstracts'], **kwargs)
    abstr['Email Address'] = [s.lower() for s in abstr['Email Address']]

    if kwargs['registered_abstracts']:
        regabs = Table.read(kwargs['registered_abstracts'], format='ascii.csv')
        #regabs['registered'] = True
        abstr = join(abstr, regabs)
        #abstr = abstr[abstr['registered']]



    ind_talk = (abstr['type'] == 'invited') | (abstr['type'] == 'contributed')
    ind_poster = abstr['type'] == 'poster'

    talks = abstr[ind_talk]
    talks.sort(['binary_time', 'type', 'idnum'])
    posters = abstr[ind_poster]
    posters['intnumber'] = [int(i) for i in posters['poster number']]
    posters.sort(['intnumber', 'First author'])

    # List all entries that do not have a valid type
    notype = abstr[~ind_talk & ~ind_poster]

    if len(notype) > 0:
        print('The following entries do not have a valid "type" entry, which would classify them as talk or poster:')
        for r in notype:
            print(r['Timestamp'], r['type'], r['Title of presentation'])

    if not kwargs['output_unassigned']:
        abstr = abstr[abstr['type'] != '']
    abstr.sort(['binary_time', 'poster number'])
    abstr['index'] = np.arange(1.0 * len(abstr))
    write_json_abstracts(abstr)

    notype['intnumber'] = [int(i) for i in notype['idnum']]
    notype.sort(['intnumber'])
    unass = notype if kwargs['output_unassigned'] else []

    return {'talks': talks, 'posters': posters, 'unassigned': unass}
