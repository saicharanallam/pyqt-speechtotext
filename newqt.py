# import sys
# # from PyQt4.QtCore import *
# # from PyQt4.QtGui import *

# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
# def window():
#    app = QApplication(sys.argv)
#    win = QWidget()
	
#    e1 = QLineEdit()
#    e1.setValidator(QIntValidator())
#    e1.setMaxLength(4)
#    e1.setAlignment(Qt.AlignRight)
#    e1.setFont(QFont("Arial",20))
	
#    e2 = QLineEdit()
#    e2.setValidator(QDoubleValidator(0.99,99.99,2))
	
#    flo = QFormLayout()
#    flo.addRow("integer validator", e1)
#    flo.addRow("Double validator",e2)
	
#    e3 = QLineEdit()
#    e3.setInputMask('+99_9999_999999')
#    flo.addRow("Input Mask",e3)
	
#    e4 = QLineEdit()
#    e4.textChanged.connect(textchanged)
#    flo.addRow("Text changed",e4)
	
#    e5 = QLineEdit()
#    e5.setEchoMode(QLineEdit.Password)
#    flo.addRow("Password",e5)
	
#    e6 = QLineEdit("Hello Python")
#    e6.setReadOnly(True)
#    flo.addRow("Read Only",e6)
	
#    e5.editingFinished.connect(enterPress)
#    win.setLayout(flo)
#    win.setWindowTitle("PyQt")
#    win.show()
	
#    sys.exit(app.exec_())

# def textchanged(text):
#    print ("contents of text box: "+text)
	
# def enterPress():
#    print ("edited")

# if __name__ == '__main__':
#    window()



















# from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
# QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
# QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
# QVBoxLayout)

# import sys

# class Dialog(QDialog):
#     NumGridRows = 3
#     NumButtons = 4

#     def __init__(self):
#         super(Dialog, self).__init__()
#         self.createFormGroupBox()
        
#         buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#         buttonBox.accepted.connect(self.accept)
#         buttonBox.rejected.connect(self.reject)
        
#         mainLayout = QVBoxLayout()
#         mainLayout.addWidget(self.formGroupBox)
#         mainLayout.addWidget(buttonBox)
#         self.setLayout(mainLayout)
        
#         self.setWindowTitle("Form Layout - pythonspot.com")
        
#     def createFormGroupBox(self):
#         self.formGroupBox = QGroupBox("Form layout")
#         layout = QFormLayout()
#         layout.addRow(QLabel("Name:"), QLineEdit())
#         layout.addRow(QLabel("Country:"), QComboBox())
#         layout.addRow(QLabel("Age:"), QSpinBox())
#         self.formGroupBox.setLayout(layout)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     dialog = Dialog()
#     sys.exit(dialog.exec_())






import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize    

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(320, 140))    
        self.setWindowTitle("") 

        self.nameLabel = QLabel(self)
        self.nameLabel.setText('Name:')
        self.line = QLineEdit(self)

        self.line.move(80, 20)
        self.line.resize(200, 32)
        self.nameLabel.move(20, 20)

        pybutton = QPushButton('OK', self)
        pybutton.clicked.connect(self.clickMethod)
        pybutton.resize(200,32)
        pybutton.move(80, 60)        

    def clickMethod(self):
        print('Your name: ' + self.line.text())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )
