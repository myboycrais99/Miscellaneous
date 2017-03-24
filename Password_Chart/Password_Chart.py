"""
pyuic5 Password_Chart.ui -o design.py
pyinstaller --onefile --path C:\\Users\\Ryan\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin Password_Chart.py
"""

import design  # This file holds our MainWindow and all design related things
               # it also keeps events etc that we defined in Qt Designer
from PyQt5 import QtGui, QtWidgets  # Import the PyQt4 module we'll need
import layout
from lxml import etree
import os
import string
import subprocess
import sys
import tempfile

# In Python2 methods are bound to QtGui while the same methods are bound to
# QtWidgets in Python3. This block of code creates a dumby object based on the
# current version of python.
try:
    QtGui.QMainWindow
    QtGui_module = QtGui

except AttributeError:
    QtGui_module = QtWidgets

if sys.version_info >= (3, 6):
    import secrets as randomizer

else:
    import random as randomizer


class PasswordChart(QtGui_module.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        # This is defined in design.py file automatically. It sets up layout and
        # widgets that are defined
        self.setupUi(self)

        self.lengths = range(3, 5)

        self.ButtonGenerate.clicked.connect(self.generate)
        self.ButtonSave.clicked.connect(self.save_chart)
        self.ButtonQuit.clicked.connect(self.exit)

    def generate(self):
        alphanumeric = string.ascii_letters + string.digits
        common = "!@#$%^&*<>"
        # advanced = "()-_+=,.?/:;[]{}"

        valid_chars = alphanumeric + common  # + advanced

        for i in range(36):
            tmp = ""
            length = randomizer.choice(self.lengths)
            for j in range(length):
                tmp += randomizer.choice(valid_chars)

            getattr(self, "label_{}".format(i)).setText(tmp)

    def save_chart(self):
        # with open("drawing.svg", "rb") as f:
        #     svg = f.read()

        # xml_data = etree.fromstring(svg)
        xml_data = etree.fromstring(layout.get_layout())
        SVGNS = u"http://www.w3.org/2000/svg"

        for i in range(36):
            tmp = getattr(self, "label_{}".format(i)).text()

            etree.ETXPath("//{%s}*[@id='label_%s']" % (SVGNS, i))(xml_data)[
                0].text = tmp

        svg = etree.tostring(xml_data)

        fd, filename = tempfile.mkstemp()
        try:
            print(filename)

            os.write(fd, svg)

            subprocess.call(
                ["C:\Program Files\Inkscape\inkscape.exe", filename,
                 "--export-png", "password_chart.png",
                 "--export-dpi", "96"])

            os.close(fd)

        except:
            pass

        finally:
            os.remove(filename)


    @staticmethod
    def exit():
        QtGui_module.QApplication.quit()


def main():
    app = QtGui_module.QApplication(sys.argv)  # A new instance of QApplication
    form = PasswordChart()      # We set the form to be our ExampleApp (design)
    form.show()                 # Show the form
    app.exec_()                 # and execute the app


if __name__ == '__main__':
    main()
    # xml_data = etree.fromstring(layout.get_layout())
