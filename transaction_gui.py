from PyQt4 import QtGui, QtCore

import pandas as pd
import datetime
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Transaction_Table(QtGui.QTableWidget):
    def __init__(self, parent, data, *args):
        QtGui.QTableWidget.__init__(self, *args)
        self.data = data
        self.set_data()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
    # end __init__

    def set_data(self):
        self.setRowCount( len(self.data) )
        self.setColumnCount( len(self.data[0] ) )

        for row, line in enumerate(self.data):
            for col, thing in enumerate(line):
                item = QtGui.QTableWidgetItem( str(thing) )
                self.setItem(row, col, item ) #TODO: Just grab the existing item instead of creating new
    # end set_data

    def filter_data(self, search_string):
        '''The search_string will be split by commas. Any row containing one of the substrings will be kept'''
        showing_rows = np.zeros( self.rowCount(), dtype=bool )
        search_strings = search_string.split(',')
        search_strings = [s for s in search_strings if len(s) > 0]
        for row in range(self.rowCount()):
            hide_row = True
            for col in range(self.columnCount()):
                txt = str(self.item( row, col ).text())
                if np.any([txt.lower().find( s) > -1 for s in search_strings]):
                    showing_rows[row] = True


        for row, show in enumerate(showing_rows):
            self.setRowHidden( row, not show )
    # end filter_data

    def show_all(self):
        for row in range(self.rowCount()):
            self.setRowHidden(row, False)

    # end show_all

    def get_showing(self):
        '''Return the showing rows'''
        indices = np.zeros(len(self.data), dtype=bool)
        for row in range(self.rowCount()):
            if not self.isRowHidden(row):
                indices[row] = True

        return [d for i, d in enumerate(self.data) if indices[i] ]
    # end get_showing
#end class Transaction_Table


class Transaction_Gui( QtGui.QMainWindow ):
    '''GUI for displaying a list of transactions, filtering the transactions, and plotting data'''
    def __init__(self, parent, data):
        super(self.__class__, self).__init__(parent)

        widget = QtGui.QWidget()

        self.figure = Figure()
        self.canvas = FigureCanvas( self.figure )
        self.ax     = self.figure.add_subplot(111)
        self.table = Transaction_Table(widget, data)
        self.entry = QtGui.QLineEdit()
        self.entry.keyPressEvent = self._on_key_pressed
        szr = QtGui.QVBoxLayout()
        szr.addWidget( self.canvas )
        szr.addWidget( self.table )
        szr.addWidget( self.entry )
        widget.setLayout( szr )
        widget.setMinimumSize(1300, 500)
        self.setCentralWidget( widget )
        self.setFocusProxy( self.entry )
        self.entry.setFocus()
        self.show()
    # end __init__

    def _on_key_pressed( self, evt ):
        QtGui.QLineEdit.keyPressEvent(self.entry, evt)
        if not evt.key() == QtCore.Qt.Key_Escape:
            self.table.filter_data( str(self.entry.text()) )
        else:
            self.entry.setText('')
            self.table.show_all()
        showing = self.table.get_showing()
        nums    = [float(s[2]) for s in showing]
        
        
        
        showing = np.array(showing)
        amounts = np.array( showing[:,2]).astype(np.float)
        dates   = [datetime.datetime.strptime( el[0], '%m/%d/%y' ).date() for el in showing]
        #ustore_dates = np.unique( store_dates )


        # Get the weekly and monthly means
        pandas_data = pd.DataFrame(showing, columns=['Date', 'Description', 'Amount'])
        pandas_data["Date"] = pd.to_datetime(pandas_data["Date"], format='%m/%d/%y')
        #pandas_data.convert_objects(convert_numeric=True)
        pandas_data['Amount'] = pandas_data['Amount'].astype(float)
        pandas_data = pandas_data.set_index( 'Date' )
        pandas_data = pandas_data.sort_index(ascending=True)
        #pandas_data["Day of the Week"] = pandas_data["Date"].dt.dayofweek
        #grouped_data = pandas_data.groupby('Day of the Week').aggregate(np.mean)

        roll_mean =[]
        date = pandas_data.index[0]
        rolling_dates = []
        while date <= pandas_data.index[-1]:
            amt = pandas_data['Amount'][date : date + pd.Timedelta('14 days')]
            roll_mean.append( amt.mean() )
            rolling_dates.append( date )
            date = date + pd.Timedelta('14 days')

        print np.mean(roll_mean)
        
        self.ax.cla()
        self.ax.plot( dates, amounts )
        self.ax.plot( rolling_dates, roll_mean, 'r' )
        self.canvas.draw()
        import matplotlib.dates as mdates
        myFmt = mdates.DateFormatter('%Y-%m-%d')
        self.ax.xaxis.set_major_formatter(myFmt)
        self.figure.autofmt_xdate()
    # end _on_key_pressed

# end class Transaction_Gui



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('csv_file')

    args = parser.parse_args()

    app = QtGui.QApplication([])

    import csv
    with open( args.csv_file, 'r') as fid:
        rdr = csv.reader( fid )
        data = []
        for row in rdr:
            data.append( row )
        
    win = Transaction_Gui(None, data[1:])

    
    app.exec_()

    
