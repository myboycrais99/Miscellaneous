"""
pyuic5 Password_Chart.ui -o design.py
pyinstaller --onefile --path C:\\Users\\Ryan\\AppData\\Local\\Programs\\Python\\
        Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin Password_Chart.py
"""

import os
import string
import subprocess
import sys
import tempfile

from lxml import etree
from PyQt5 import QtGui, QtWidgets  # Import the PyQt4 module we'll need

import design  # This file holds our MainWindow and all design related things
               # it also keeps events etc that we defined in Qt Designer

import layout

# In Python2 methods are bound to QtGui while the same methods are bound to
# QtWidgets in Python3. This block of code creates a dumby object based on the
# current version of python.
try:
    QtGui.QMainWindow
    QT_GUI = QtGui

except AttributeError:
    QT_GUI = QtWidgets

if sys.version_info >= (3, 6):
    import secrets as randomizer

else:
    import random as randomizer


class PasswordChart(QT_GUI.QMainWindow, design.Ui_MainWindow):
    """This class creates a GUI mapping a random length of characters to the
    alphabet and ten digits"""

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
        """This method defines the lengths of characters and the valid
        characters for use in the password chart then updates the GUI with the
        randomly generated characters.

        :return:
        None
        """

        alphanumeric = string.ascii_letters + string.digits
        common = "!@#$%^&*<>"
        # advanced = "()-_+=,.?/:;[]{}"

        valid_chars = alphanumeric + common  # + advanced

        for i in range(36):
            tmp = ""
            length = randomizer.choice(self.lengths)
            for _ in range(length):
                tmp += randomizer.choice(valid_chars)

            getattr(self, "label_{}".format(i)).setText(tmp)

    def save_chart(self):
        """This method uses a pre-defined XML layout and adds the random strings
        generated above and then saves the password chart as a png.

        :return:
        None
        """

        xml_data = etree.fromstring(layout.get_layout())

        for i in range(36):
            tmp = getattr(self, "label_{}".format(i)).text()

            etree.ETXPath("//{%s}*[@id='label_%s']" % (
                u"http://www.w3.org/2000/svg", i))(xml_data)[0].text = tmp

        svg = etree.tostring(xml_data)

        file_handle, filename = tempfile.mkstemp()
        try:
            os.write(file_handle, svg)

            subprocess.call(
                # Default location of inkscape x64. Change if inkscape is
                # installed in a separate location
                [r"C:\Program Files\Inkscape\inkscape.exe", filename,
                 "--export-png", "password_chart.png",
                 "--export-dpi", "96"])

            os.close(file_handle)

        finally:
            os.remove(filename)


    @staticmethod
    def exit():
        """Close the qui"""
        QT_GUI.QApplication.quit()


def main():
    """Launch main program"""
    app = QT_GUI.QApplication(sys.argv)  # A new instance of QApplication
    form = PasswordChart()      # We set the form to be our ExampleApp (design)
    form.show()                 # Show the form
    app.exec_()                 # and execute the app


if __name__ == '__main__':
    main()
