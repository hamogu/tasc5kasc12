from astropy.table import Table


def data(**kwargs):
    return {'reglist': Table.read('data/reglist.csv')}
