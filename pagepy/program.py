from astropy.table import Table, vstack

import pagepy.abstracts as abstracts


def data(**kwargs):

    absdata = abstracts.data(**kwargs)
    extraschedule = Table.read('data/schedule.csv', format='csv')
    extraschedule['binary_time'] = [abstracts.parse_day_time(r['day'], r['time']) for r in extraschedule]
    extraschedule['type'] = 'schedule'
    for col in ['First author', 'topic']:
        extraschedule[col] = ''

    coltouse = ['type', 'time', 'day', 'binary_time', 'First author',
                'Title of presentation', 'topic']
    timetab = vstack([extraschedule[coltouse], absdata['talks'][coltouse]])
    timetab.sort('binary_time')
    days  = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    dnames = {s[:3]: '{0}: {2}/{3}/{1}'.format(s, *abstracts.dates[s[:3]]) for s in days}
    prog = [(dnames[d[:3]], timetab[timetab['day'] == d[:3]]) for d in days]

    return {'data': prog}
