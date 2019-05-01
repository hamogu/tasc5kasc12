import argparse

parser = argparse.ArgumentParser(description='Generate webpages for TASC5. We want to generate statics pages for simplicity, but might read in some database (e.g. the database of abstracts) when doing so.')
parser.add_argument('outpath',
                    help='base directory for output')
parser.add_argument('-a', '--abstracts',
                    default='../abstracts.csv',
                    help='csv file with abstracts')
parser.add_argument('--output-unassigned', action='store_true',
                    help='Output presentations that do not have a "type" entry in the table')
parser.add_argument('--autoacceptposters', action='store_true',
                    help='Automatically add type "poster" for all contributiosn submitted as poster')
parser.add_argument('-r', '--registered-abstracts',
                    help='csv file with author and title for all abstracts from REGISTERED authors. Only abstracts that are in the abstracts table AND in this list will be processed.')
