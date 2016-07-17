from PyQt4 import QtGui, QtCore

import numpy as np



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
        for row in range(self.rowCount()):
            hide_row = True
            for col in range(self.columnCount()):
                txt = str(self.item( row, col ).text())
                if txt.lower().find( search_string) > -1:
                    print txt
                    hide_row = False

            if hide_row:
                self.setRowHidden( row, hide_row )
    # end filter_data

    def show_all(self):
        for row in range(self.rowCount()):
            self.setRowHidden(row, False)
                    
#end class Transaction_Table


class Transaction_Gui( QtGui.QMainWindow ):
    '''GUI for displaying a list of transactions, filtering the transactions, and plotting data'''
    def __init__(self, parent, data):
        super(self.__class__, self).__init__(parent)

        widget = QtGui.QWidget()
        
        self.table = Transaction_Table(widget, data)
        self.entry = QtGui.QLineEdit()
        def keyPressed( evt ):
            QtGui.QLineEdit.keyPressEvent(self.entry, evt)
            if not evt.key() == QtCore.Qt.Key_Escape:
                print evt.text()
                self.table.filter_data( str(self.entry.text()) )
            else:
                self.entry.setText('')
                self.table.show_all()
        # end keyPressed
        self.entry.keyPressEvent = keyPressed
        szr = QtGui.QVBoxLayout()
        szr.addWidget( self.table )
        szr.addWidget( self.entry )
        widget.setLayout( szr )
        self.setCentralWidget( widget )
        self.show()
    # end __init__
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
        
    win = Transaction_Gui(None, data)

    
    app.exec_()

    
