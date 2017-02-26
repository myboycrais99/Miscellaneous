"""
pyinstaller --path C:\\Python35-32\\Lib\\site-packages\\PyQt5\\Qt\\bin Modify_JPG_Metadata.py
pyinstaller --path C:\\Users\\Ryan\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages\\PyQt5\\Qt\\bin Modify_JPG_Metadata.py
"""

import piexif
from PyQt5 import QtGui, QtWidgets  # Import the PyQt4 module we'll need
import sys  # We need sys so that we can pass argv to QApplication
import design  # This file holds our MainWindow and all design related things
               # it also keeps events etc that we defined in Qt Designer

try:
    QtGui.QMainWindow
    QtGui_module = QtGui

except AttributeError:
    QtGui_module = QtWidgets


class ModifyApp(QtGui_module.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
                            # It sets up layout and widgets that are defined

        self.COPYRIGHT = 33432
        self.CLASSIFICATION = 37394
        self.TAGS = 40094

        self.images = None

        self.ButtonSelectImages.clicked.connect(self.browse_folder)
        self.ButtonCancel.clicked.connect(self.exit)
        self.ButtonApply.clicked.connect(self.modify_metadata)

    def browse_folder(self):
        images = QtGui_module.QFileDialog.getOpenFileNames(
            self,
            caption="Select one or more JPGs to modify",
            filter="Images (*.jpg);;All Files (*.*)",
            )[0]
        self.images = images
        num = len(images)
        if num == 1:
            self.LabelSelected.setText("1 pictures selected")
        else:
            self.LabelSelected.setText("{0} pictures selected".format(num))

    def modify_metadata(self):

        if self.images is not None:
            for picture in self.images:

                exif = piexif.load(picture)

                zeroth_ifd = exif["0th"]

                # Add copyright
                copyright_str = self.TextCopyright.text()
                zeroth_ifd[self.COPYRIGHT] = bytes(copyright_str, "utf-8")

                # Add classification
                classification = self.ComboClassification.currentText()
                zeroth_ifd[self.CLASSIFICATION] = bytes(classification, "utf-8")

                # Add tags
                tags = self.TextTags.text()
                if not isinstance(tags, list):
                    tags = tags.lower().split(";")

                if not self.CheckBoxRemove.checkState():
                    try:
                        curr_tags = bytes(
                            zeroth_ifd[self.TAGS]).decode("utf-16")
                        curr_tags = curr_tags.split(";")

                        tags = list(set([x.lower() for x in curr_tags + tags]))

                    except KeyError:
                        pass

                new_tag = tags[0]
                for tag in tags[1:]:
                    new_tag += ";" + tag

                zeroth_ifd[self.TAGS] = bytes(new_tag, "utf-16")

                # Recombine dictionaries into binary format
                exif_bytes = piexif.dump({
                                          "0th": zeroth_ifd,
                                          })

                # Insert EXIF data into JPG
                piexif.insert(exif_bytes, picture)

    @staticmethod
    def exit():
        QtGui_module.QApplication.quit()


def main():
    app = QtGui_module.QApplication(sys.argv)  # A new instance of QApplication
    form = ModifyApp()         # We set the form to be our ExampleApp (design)
    form.show()                 # Show the form
    app.exec_()                 # and execute the app


if __name__ == '__main__':
    main()
