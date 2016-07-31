#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser(__doc__)
parser.add_argument( 'history_file', help='csv file to read bank history from' )
parser.add_argument( '--unassigned', help = 'If specified, ungrouped items will be written to unassigned.csv', action='store_true')
args = parser.parse_args()


import matplotlib
#matplotlib.use('wxagg')
import ipdb


import numpy as np
import csv
data = []
with open( args.history_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        data.append(row)


ndata = np.array(data[1:])


stores = {'kohls' : ['kohls'],
          'grocery' : ['hannaford', 'newberry farms', 'trader joe', 'applecrest'],
          'home'    : ['netflix', 'aubuchon', 'exeter lumber', 'good juju', 'michaels stores', 'service experts'],
          #'mortgage' : ['nationstar'],
          'insurance' : ['liberty mutual'],
          'amazon' : ['amazon'],
          'verizon' : ['verizon'],
          'target' : ['target'],
          #'comcast' : ['comcast'],
          #'arjay'   : ['arjay hardware'],
          ##'netflix' : ['netflix'],
          #'big bean' : ['big bean cafe'],
          #'electric' : ['PSNH', 'eversource'],
          #'gym'      : ['seacoast sports clubs'],
          'clothes' : ['comenity'], #Loft card
          'health' : ['tranquility salon'],
          'car' : ['subaru', ' ford', 'car wash', 'e z pass'],
          'subaru' : ['subaru'],
          'gas' : ['newmarket minimart', 'sunoco', 'exxonmobil'],
          'utilities' : ['comcast', 'eversource', 'richard'],
          'Eating out' : ['pad thai', 'chipotle', 'riverwalk', 'the big bean cafe', 'five guys', 'bae can', 'bae mer 15', 'uhs retail', 'unh dining id office', 'uhs dining', 'ffrost sawyer tavern', 'paulys pocket', 'northern embers', 'd squared', 'flatbread company', 'works bakery', 'green bean', 'seedling cafe', 'newfields country store']}

transactions = {}
np_data = np.array(data[1:])
unused_rows = np.ones( np_data.shape[0], dtype=bool )
for store_name, keywords in stores.items():
    entries = []
    for row_i, row in enumerate(data[1:]):
        for key in keywords:
            if row[1].lower().find(key) >= 0:
                entries.append(row)
                unused_rows[ row_i ] = False
                break#TODO: Catch case where item matches multiple categories
    transactions[store_name] = entries

# Write out the unused entries
if args.unassigned == True:
    with open( 'unassigned.csv', 'w') as f:
        writer = csv.writer( f )
        writer.writerows( np_data[unused_rows,:] )


blah = np_data[unused_rows,1].copy()
blah.sort()
#print blah
#exit(0)
import datetime
import matplotlib.pyplot as plt


def onpick( event ):
    '''Show the data for the line that is clicked on'''
    idx = -1
    try:
        idx = ax1.lines.index(event.artist)
    except:
        pass
    print 'idx = {0}'.format(idx)

                            

''' 
hannaford = np.array(transactions['hannaford'])
hannaford_nums = np.array(hannaford[:,2]).astype(np.float)

hannaford_dates = [datetime.datetime.strptime( el[0], '%m/%d/%y' ).date() for el in hannaford]


_=plt.plot(hannaford_dates, hannaford_nums)
plt.show()
'''
#ipdb.set_trace()
summaries = {}
for key, val in transactions.items():
    if len(val) == 0:
        print 'nothing for {0}'.format( key )
        continue

    store_data    = np.array(val)
    store_amounts = np.array(store_data[:,2]).astype(np.float)
    store_dates   = [datetime.datetime.strptime( el[0], '%m/%d/%y' ).date() for el in store_data]
    ustore_dates = np.unique( store_dates )
    amounts = []
    for d in ustore_dates:
        inds = ustore_dates == d
        amount = store_amounts[inds].sum()
        amounts.append( amount )
        
    '''
    # WARNING: ASSUMES SINGLE YEAR WORTH OF DATA
    months = np.array( [s.month for s in store_dates ] )
    unique_months = np.unique( months )
    amounts = []
    for month in unique_months:
        inds = months == month
        amount = store_amounts[ inds ].sum()
        amounts.append( amount )
    '''
    print '{0}: \t\t{1}'.format( key, store_amounts.sum() )
    #_=plt.plot(store_dates, store_amounts, '*-')
    #plt.plot( unique_months, amounts, '*-' )
    plt.plot( ustore_dates, amounts )
    #plt.bar( unique_months, amounts )
l = plt.legend( [key for key,val in transactions.items() if len(val)>0])    
l.draggable(True)
#ipdb.set_trace()

import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%Y-%m-%d')
plt.gca().xaxis.set_major_formatter(myFmt)

#ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
plt.gcf().autofmt_xdate()
#mng = plt.get_current_fig_manager()
#mng.frame.Maximize(True)

plt.show()


