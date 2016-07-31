#!/usr/bin/env python
'''
Converts a bankg statement in pdf to csv format
'''
import ipdb
import csv
import numpy as np
import argparse
parser = argparse.ArgumentParser(__doc__)
parser.add_argument('input_file', help='input banking statement that has been converted format')
parser.add_argument('output_file', help='output csv file' )

args = parser.parse_args()

import subprocess
intermediate = args.input_file + '.intermediate'
subprocess.call(['pdftotext', args.input_file, intermediate, '-layout'])


lines = []
with open( intermediate, 'r') as f:
    lines = f.readlines()

orig_lines = lines[:]

# Find first occurance of DAILY ACCOUNT ACTIVITY followed by 'Electronic Payments' to indicate start
# and first occurance of DAILY BALANCE SUMMARY to indicate end
first_stage = True
for idx, line in enumerate( lines ):
    if not first_stage and line.startswith( 'Electronic Payments' ):
        start_idx = idx
        break
    if line.startswith( 'DAILY ACCOUNT ACTIVITY' ):
        first_stage = False

for idx, line in enumerate( lines ):
    if line.startswith( 'DAILY BALANCE SUMMARY' ):
        end_idx = idx
        break


lines = lines[start_idx:end_idx]
data = []
for idx, line in enumerate(lines[:-1]):
    if len(line) > 2 and (line[1] == '/' or line[2] == '/'):
        entry       = [thing for thing in line.strip().replace('"','').split('  ') if len(thing) > 0]
        # Often there is more detail to the description on the next line, but
        # sometimes it is another entry. Here I am assuming that more detail would start with a bunch of blank space
        if len(lines[idx+1]) > 0 and lines[idx+1].startswith('    '):
            description = ' '.join( lines[idx+1].split() )
        else:
            description = ''
        entry[1]    += ', ' + description
        #Note that there are commas in entry[1], so quotes will be inserted around it in the write-out
        data.append( entry )

data = np.array( data )


import datetime
# Try to find the year in the input filename
for i in range(len(args.input_file)-4):
    try:
        year = int(args.input_file[i:i+4])
        if year > 0:
            break
    except:
        continue
    
    
print 'Year extracted from filename as {0}'.format( year )
year = str(year)
for i in range( data.shape[0] ):
    data[i,0] = data[i,0] + '/' + year[2:]
dates   = np.array( [datetime.datetime.strptime( el[0], "%m/%d/%y" ).date().toordinal() for el in data] )

# Remove commas from amounts and sort the data by date and amount
# NOTE: Amounts are positive here (they are in the payments section), so we throw a minus sign in front before write-out
amounts = -np.array( [el.replace(',','') for el in data[:,2]] ).astype(np.float)
data[:,2] = amounts
inds    = np.lexsort( (amounts, dates) )
dsorted = data[ inds[::-1], :]


# Recalc dates and amounts with sorted data
#dates   = np.array( [datetime.datetime.strptime( el[0], "%m/%d/%y" ).date().toordinal() for el in dsorted] )
#amounts = np.array( [el.replace(',','') for el in dsorted[:,2]] ).astype(np.float)


# Write-out to a file
with open( args.output_file, 'w' ) as o:
    writer = csv.writer( o )
    writer.writerow( ['Date', 'Description', 'Amount'] )
    writer.writerows( dsorted )
    



