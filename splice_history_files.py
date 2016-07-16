#!/usr/bin/env python
'''
Splice two bank history csv files, removing duplicate lines (if any)
'''
import numpy as np
import csv
import datetime


def read_hist_file( filename ):
    data = []
    with open( filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    hdr = data[0]
    data = np.array(data[1:])
    return hdr, data

    
def splice_files( file1, file2 ):
    '''Splices the two input files, returning the result in a numpy array'''
    hdr1, data1 = read_hist_file( file1 )
    hdr2, data2 = read_hist_file( file2 )

    # 1. Concatenate the arrays
    # 2. Get the dates
    # 3. Sort the array by date and amount
    # 4. Remove duplicates
    data    = np.concatenate( (data1, data2), axis=0 )
    dates   = np.array( [datetime.datetime.strptime( el[0], "%m/%d/%y" ).date().toordinal() for el in data] )
    amounts = data[:,2].astype(np.float)
    inds    = np.lexsort( (amounts, dates) )
    dsorted = data[ inds[::-1], :]

    # Recalc dates and amounts with sorted data
    dates   = np.array( [datetime.datetime.strptime( el[0], "%m/%d/%y" ).date().toordinal() for el in dsorted] )
    amounts = dsorted[:,2].astype(np.float)
    
    # Remove duplicates
    #import ipdb; ipdb.set_trace()
    dup_inds = np.zeros( len(dsorted), dtype=bool )
    for i1 in range(len(dsorted) ):
        for i2 in range( i1+1, len(dsorted) ):
            if dates[i1] != dates[i2]:
                break
            if (amounts[i1] == amounts[i2]) and (dsorted[i1,1] == dsorted[i2,1]):
                dup_inds[i1] = True

    print '{0} duplicates found'.format( np.sum( dup_inds ) )
    dsorted = dsorted[ np.logical_not( dup_inds ), :]
    return hdr1, dsorted


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument( 'in_file1' )
    parser.add_argument( 'in_file2' )
    parser.add_argument( 'outfile' )

    args = parser.parse_args()

    hdr, d = splice_files( args.in_file1, args.in_file2 )
    with open( args.outfile, 'w') as f:
        writer = csv.writer( f )
        writer.writerow( hdr )
        writer.writerows( d )

    
