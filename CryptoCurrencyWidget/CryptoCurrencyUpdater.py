import base64
import json
import os
import sys
import time
import tempfile
import urllib.request

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, \
    QHBoxLayout, QGridLayout, QLabel, QLineEdit, QAction, QCheckBox, qApp, \
    QWidget, QScrollArea
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

import resources

"""
This program uses the CoinMarketCap API to retrieve and display information
about various crypto currencies in a small applet.


CoinMarketCap JSON API Documentation v1: https://coinmarketcap.com/api/

Ticker
    *Endpoint: /ticker/
    *Method: GET
    *Optional parameters:
        (int) start - return results from rank [start] and above
        (int) limit - return a maximum of [limit] results (default is 100,
            use 0 to return all results)
        (string) convert - return price, 24h volume, and market cap in terms of
            another currency. Valid values are: "AUD", "BRL", "CAD", "CHF",
            "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR",
            "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP",
            "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR"

    *Example: https://api.coinmarketcap.com/v1/ticker/
    *Example: https://api.coinmarketcap.com/v1/ticker/?limit=10
    *Example: https://api.coinmarketcap.com/v1/ticker/?start=100&limit=10
    *Example: https://api.coinmarketcap.com/v1/ticker/?convert=EUR&limit=10

    *Output
        {
            {
                "id": "bitcoin",
                "name": "Bitcoin",
                "symbol": "BTC",
                "rank": "1",
                "price_usd": "573.137",
                "price_btc": "1.0",
                "24h_volume_usd": "72855700.0",
                "market_cap_usd": "9080883500.0",
                "available_supply": "15844176.0",
                "total_supply": "15844176.0",
                "percent_change_1h": "0.04",
                "percent_change_24h": "-0.3",
                "percent_change_7d": "-0.57",
                "last_updated": "1472762067"
            }
        }

Ticker (Specific Currency)
    *Endpoint: /ticker/{id}/
    *Method: GET
    *Optional parameters:
        (string) convert - return price, 24h volume, and market cap in terms of
                another currency. Valid values are: "AUD", "BRL", "CAD", "CHF",
                "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR",
                "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP",
                "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR"
    *Example: https://api.coinmarketcap.com/v1/ticker/bitcoin/
    *Example: https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=EUR

Global Data
    *Endpoint: /global/
    *Method: GET
    *Optional parameters:
        (string) convert - return 24h volume, and market cap in terms of another
        currency. Valid values are: "AUD", "BRL", "CAD", "CHF", "CLP", "CNY",
        "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY",
        "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK",
        "SGD", "THB", "TRY", "TWD", "ZAR"
    *Example: https://api.coinmarketcap.com/v1/global/
    *Example: https://api.coinmarketcap.com/v1/global/?convert=EUR

    *Output
        {
            "total_market_cap_usd": 201241796675,
            "total_24h_volume_usd": 4548680009,
            "bitcoin_percentage_of_market_cap": 62.54,
            "active_currencies": 896,
            "active_assets": 360,
            "active_markets": 6439,
            "last_updated": 1509909852
        }
"""

"""
Update pyinstaller with pip install pyinstaller
If running in virtual environment, within PyCharm open python terminal
View -> Tools Window -> Terminal
pyinstaller --onefile --windowed --icon=logo.ico CryptoCurrencyUpdater.py
"""

__version__ = "1.0"


class GetCoinNames(QObject):
    """This thread returns num_coins number of coins. Recommend returning all
    coins"""
    coin_names_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_url = "https://api.coinmarketcap.com/v1/ticker/"

    @pyqtSlot(name="start")
    def start(self):
        pass

    @QtCore.pyqtSlot(int, name="getCoinNames")
    def get_coin_names(self, num_coins):
        with urllib.request.urlopen(self.root_url + "?limit={}"
                                    "".format(num_coins)) as url:
            data = json.loads(url.read().decode())
            tmp_names = list()

            for i in data:
                tmp_names.append(i["id"])

            self.coin_names_signal.emit(tmp_names)


class GetCoinData(QObject):
    """This thread will fetch the data for the given coin name"""
    coin_data_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_url = "https://api.coinmarketcap.com/v1/ticker/"
        self._looping = False
        self._update_frequency = 5 * 60

    @pyqtSlot(name="start")
    def start(self):
        self.get_coin_data()

    @QtCore.pyqtSlot(int, name="getCoinData")
    def get_coin_data(self):
        """
        This function gets all data for all coins and returns a dict with the
        coin rank as the dict key. The thread updates regularly based on update
        frequency.
        """
        self._looping = True
        while self._looping:
            with urllib.request.urlopen(self.root_url + "?limit=0") as url:
                data = json.loads(url.read().decode())
                tmp_data = dict()

                for i in data:
                    tmp_data[int(i["rank"])] = i

                self.coin_data_signal.emit(tmp_data)
                time.sleep(self._update_frequency)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.main_widget = MainWidget(self)
        self.select_window = SelectCoins(self)

        self.logo_jpg = resources.logo_jpg
        self.logo = tempfile.NamedTemporaryFile(delete=False)
        self.logo.write(base64.decodebytes(self.logo_jpg))
        self.logo.close()

        self.setWindowTitle("Ryan's CoinWatcher")

        self.setWindowIcon(QtGui.QIcon(self.logo.name))
        self.main_widget.setWindowIcon(QtGui.QIcon(self.logo.name))
        self.select_window.setWindowIcon(QtGui.QIcon(self.logo.name))

        self.__controls()
        self.__layout()
        self.__signals()

    def __controls(self):
        self._exit_png = resources.exit_png
        self._exit = tempfile.NamedTemporaryFile(delete=False)
        self._exit.write(base64.decodebytes(self._exit_png))
        self._exit.close()

        self._exit_act = QAction(QtGui.QIcon(self._exit.name), "Exit", self)
        self._exit_act.setShortcut("Ctrl+Q")
        self._exit_act.setStatusTip("Exit application")
        self._exit_act.triggered.connect(qApp.closeAllWindows)

        self._logo_ico = resources.logo_ico
        self._icon = tempfile.NamedTemporaryFile(delete=False)
        self._icon.write(base64.decodebytes(self._logo_ico))
        self._icon.close()

        self._selec_act = QAction(QtGui.QIcon(self._icon.name), "Select", self)
        self._selec_act.setShortcut("Ctrl+E")
        self._selec_act.setStatusTip("Select Coins")
        self._selec_act.triggered.connect(self._coin)

        self._about_ico = resources.about_png
        self._about = tempfile.NamedTemporaryFile(delete=False)
        self._about.write(base64.decodebytes(self._about_ico))
        self._about.close()

        self._about_act = QAction(QtGui.QIcon(self._about.name), "About", self)
        self._about_act.setShortcut("Ctrl+Shift+A")
        self._about_act.setStatusTip("About")
        self._about_act.triggered.connect(self._show_about)

    def __layout(self):
        _widget = QWidget(self)
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.main_widget)
        self.setCentralWidget(_widget)

        main_menu = self.menuBar()

        file_menu = main_menu.addMenu("File")
        file_menu.addAction(self._exit_act)

        edit_menu = main_menu.addMenu("Edit")
        edit_menu.addAction(self._selec_act)

        about_menu = main_menu.addMenu("About")
        about_menu.addAction(self._about_act)

        tmp_width = 0
        for k, v in self.main_widget.coin_fields.items():
            tmp_width += int(v["width"])

        self.setGeometry(400, 400, tmp_width, 250)

    def __signals(self):
        # Receive signal from main widget containing list of coin names to
        # populate check boxes
        self.main_widget.coin_names.connect(self.select_window.set_coin_names)
        self.main_widget.coin_names.emit(self.main_widget.coins)

        # Receive signal from SelectCoin widget containing dict of selected
        # coins to populate MainWidget
        self.select_window.selected_coins_signal.connect(self.main_widget.dummy)

    def _coin(self):
        # Display SelectCoin window
        self.select_window.show()

    def _show_about(self):
        self.about_window = AboutWidget(self)
        self.about_window.setWindowIcon((QtGui.QIcon(self.logo.name)))
        self.about_window.show()

    def closeEvent(self, event):
        """
        Override method so that closing MainWidget while SelectCoin window is
        open does not crash program.
        """
        self.select_window.destroy()
        event.accept()
        os.remove(self.logo.name)
        qApp.quit()


class MainWidget(QWidget):
    coin_names = pyqtSignal(list)

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)

        # Container Widget
        self.widget = QWidget()
        self.grid_widget = QWidget()

        self.coins = []
        self.selected_coins = []
        self.coin_data = []
        self.coin_boxes = []
        self.num_cols = []

        self.font_size = 14
        self.row_height = self.font_size + 12  # 24

        self.coin_fields = {
            "name": {"text": "Name", "width": int(100 * self.font_size / 8)},
            "symbol": {"text": "Symbol", "width": int(50 * self.font_size / 8)},
            "price_usd": {"text": "Price",
                          "width": int(75 * self.font_size / 8)},
            "percent_change_24h": {"text": "24h Change",
                                   "width": int(85 * self.font_size / 8)}
            }

        self.__controls()
        self.__layout()

        self._worker_name = GetCoinNames()
        self._thread_name = QtCore.QThread()
        self._worker_name.moveToThread(self._thread_name)
        self._thread_name.started.connect(self._worker_name.start)

        self._worker_data = GetCoinData()
        self._thread_data = QtCore.QThread()
        self._worker_data.moveToThread(self._thread_data)
        self._thread_data.started.connect(self._worker_data.start)

        # Number of coins to retrieve
        self.N = 0  # 0 = get all coins

        self.init_ui()
        self.dummy(names={})

    def __controls(self):
        pass

    def __layout(self):
        self.layout = QVBoxLayout()
        self.grid = QGridLayout()

        self.grid_widget.setLayout(self.grid)
        # self.grid_widget.setContentsMargins(0, 0, 0, 0)
        # self.setContentsMargins(0, 0, 0, 0)

        # Scroll Area Properties
        self.scroll = QScrollArea()

        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(False)
        self.scroll.setWidget(self.grid_widget)

        # Scroll Area Layer add
        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.scroll)
        self.vLayout.setContentsMargins(0, 0, 0, 0)

        tmp_width = 0
        for k, v in self.coin_fields.items():
            tmp_width += int(v["width"])

        self.setLayout(self.vLayout)

    def init_ui(self):
        self._worker_name.coin_names_signal.connect(self.get_coins)
        self._worker_data.coin_data_signal.connect(self.update_coin_data)

        self._thread_name.start()
        self._thread_data.start()
        qApp.processEvents()

        # Get N-number of coins worth of data
        self._worker_name.get_coin_names(self.N)

    def clear_coin_boxes(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

    def update_coin_boxes(self):
        self.clear_coin_boxes()

        # Create text boxes
        # TODO: Add menu item to select which data to show and then set the number of cols to tha number of fields selected
        self.num_cols = self.coin_fields

        tmp_cnt = 0
        for i, field in enumerate(self.coin_fields):
            self.coin_boxes.append(QLabel(self))
            self.coin_boxes[tmp_cnt].setText(self.coin_fields[field]["text"])

            self.coin_boxes[tmp_cnt].setFixedWidth(
                self.coin_fields[field]["width"])

            self.coin_boxes[tmp_cnt].setFixedHeight(self.font_size * 2)

            self.grid.addWidget(self.coin_boxes[tmp_cnt], 0, i)
            font = self.coin_boxes[tmp_cnt].font()
            font.setPointSize(self.font_size)
            font.setBold(True)
            self.coin_boxes[tmp_cnt].setFont(font)
            tmp_cnt += 1

        tmp_color = "black"
        for idx, coin_idx in enumerate(sorted(self.selected_coins)):
            if float(self.coin_data[coin_idx]["percent_change_24h"]) > 0:
                tmp_color = "green"
            elif float(self.coin_data[coin_idx]["percent_change_24h"]) < 0:
                tmp_color = "red"

            for j, field in enumerate(self.coin_fields):
                self.coin_boxes.append(QLabel(self))

                self.coin_boxes[tmp_cnt].setText(
                    "<font color={}>{:s}</font>".format(
                        tmp_color, self.coin_data[coin_idx][field]))

                self.coin_boxes[tmp_cnt].setFixedWidth(
                    self.coin_fields[field]["width"])

                self.coin_boxes[tmp_cnt].setFixedHeight(self.font_size * 2)

                font = self.coin_boxes[tmp_cnt].font()
                font.setPointSize(self.font_size)
                self.coin_boxes[tmp_cnt].setFont(font)
                self.grid.addWidget(self.coin_boxes[tmp_cnt], idx + 1, j)

                tmp_cnt += 1

        tmp_width = 0
        for k, v in self.coin_fields.items():
            tmp_width += int(v["width"])

        self.grid_widget.setGeometry(0, 0, tmp_width,
                                     (len(self.selected_coins) + 1) *
                                     self.row_height + 10)

    def get_names(self):
        pass

    @QtCore.pyqtSlot(list, name="getCoins")
    def get_coins(self, names):
        self.coins = names

    @QtCore.pyqtSlot(dict, name="dummy")
    def dummy(self, names):
        """
        Function takes in a dictionary of coin names that use their market cap
        ranking as an index
        """
        self.selected_coins = names
        self.update_coin_boxes()

    @QtCore.pyqtSlot(dict, name="updateCoinData")
    def update_coin_data(self, coin_data):
        self.coin_data = coin_data
        self.update_coin_boxes()


class SelectCoins(QtWidgets.QWidget):
    """
    GUI window that presents a list of coins for the user to select and returns
    the selected coin names to the main GUI.
    """
    selected_coins_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super(SelectCoins, self).__init__()

        # Container Widget
        self.widget = QWidget()
        self.grid_widget = QWidget()

        self.__controls()
        self.__layout()

        self.coins = []
        self.coin_names = []
        self.selected_coins = dict()

        self.num_cols = 4
        self.col_width = 150
        self.row_height = 24
        self.setGeometry(200, 100, self.num_cols * self.col_width,
                         self.row_height * 10)

    def __controls(self):
        self.label_num_coins = QLabel("Number of Coins")
        self.label_num_coins.setFixedWidth(100)
        self.edit_num_coins = QLineEdit()
        self.edit_num_coins.setText("10")
        self.edit_num_coins.setFixedWidth(50)
        self.edit_num_coins.textChanged.connect(self.update_grid)

        self.label_coin_index = QLabel("Start Index")
        self.label_coin_index.setFixedWidth(100)
        self.edit_coin_index = QLineEdit()
        self.edit_coin_index.setText("1")
        self.edit_coin_index.setFixedWidth(50)
        self.edit_coin_index.textChanged.connect(self.update_grid)

    def __layout(self):
        self.layout = QVBoxLayout()
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.grid = QGridLayout()

        self.hbox.addWidget(self.label_num_coins, alignment=QtCore.Qt.AlignLeft)
        self.hbox.addWidget(self.edit_num_coins, alignment=QtCore.Qt.AlignLeft)

        self.hbox.addWidget(self.label_coin_index,
                            alignment=QtCore.Qt.AlignLeft)
        self.hbox.addWidget(self.edit_coin_index,
                            alignment=QtCore.Qt.AlignLeft)

        self.vbox.addLayout(self.hbox)

        self.widget.setLayout(self.vbox)
        self.grid_widget.setLayout(self.grid)

        # Scroll Area Properties
        self.scroll = QScrollArea()

        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(False)
        self.scroll.setWidget(self.grid_widget)

        # Scroll Area Layer add
        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.widget)
        self.vLayout.addWidget(self.scroll)

        self.setLayout(self.vLayout)

    def initialize_grid(self):
        row_cnt = 0
        for i in range(len(self.coin_names)):

            if i % self.num_cols == 0:
                row_cnt += 1

            self.coins.append(QCheckBox(self))
            self.coins[i].setText("{}: {:s}".format(i + 1,
                                                    self.coin_names[i]))
            self.coins[i].setObjectName("{}".format(self.coin_names[i]))

            self.coins[i].stateChanged.connect(self.selected)
            self.coins[i].setFixedWidth(self.col_width)

            self.grid.addWidget(self.coins[i], row_cnt, i % self.num_cols,
                                alignment=QtCore.Qt.AlignLeft)

    def clear_grid(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)

    def update_grid(self):
        self.clear_grid()

        start_idx = int(self.edit_coin_index.text())
        num_coins_to_show = int(self.edit_num_coins.text())
        num_coins_total = len(self.coin_names)

        if (not self.edit_num_coins.text() in ["", "0"]
                and not self.edit_coin_index.text() in ["", "0"]):

            if num_coins_to_show > num_coins_total - start_idx:
                num_coins_to_show = num_coins_total - (start_idx - 1)

            row_cnt = 0
            if not self.coins:
                self.initialize_grid()
                self.update_grid()

            else:
                i = 0
                for i in range(num_coins_to_show):

                    if i % self.num_cols == 0:
                        row_cnt += 1

                    self.grid.addWidget(self.coins[i + start_idx - 1], row_cnt,
                                        i % self.num_cols,
                                        alignment=QtCore.Qt.AlignLeft)

                if not (i + 1) % self.num_cols == 0:
                    blank = QLabel("")
                    blank.setFixedWidth(self.col_width)
                    self.grid.addWidget(blank, row_cnt,
                                        i % self.num_cols + 1, 1,
                                        self.num_cols - (
                                                (i + 1) % self.num_cols))

                self.grid_widget.setGeometry(0, 0,
                                             self.num_cols * self.col_width,
                                             row_cnt * self.row_height + 10)

    @QtCore.pyqtSlot(list, name="setCoinNames")
    def set_coin_names(self, names):
        self.coin_names = names
        self.initialize_grid()
        self.update_grid()

    def selected(self, state):
        """
        When a coin checkbox is checked this function adds the coin index and
        name to the dictionary or removes the coin if unselected.
        """
        idx, name = self.sender().text().split(":")
        idx = int(idx)

        if state == QtCore.Qt.Checked:
            self.selected_coins[idx] = name
        elif state == QtCore.Qt.Unchecked:
            del self.selected_coins[idx]

        # Emit currently selected coins to MainWindow
        self.selected_coins_signal.emit(self.selected_coins)


class AboutWidget(QtWidgets.QWidget):
    """
    Displays information about this application.
    """

    def __init__(self, parent):
        super(AboutWidget, self).__init__()
        self.setWindowTitle("Ryan's CoinWatcher")

        self.setWindowTitle("About")
        # self.setWindowIcon(QtGui.QIcon(self.logo.name))

        self.__controls()
        self.__layout()

    def __controls(self):
        self.label_about = QLabel(self)

        self._splash_png = resources.splash_png
        self._splash = tempfile.NamedTemporaryFile(delete=False)
        self._splash.write(base64.decodebytes(self._splash_png))
        self._splash.close()

        _splash = QtGui.QPixmap(self._splash.name)
        self.label_about.setPixmap(_splash)
        self.resize(_splash.width(), _splash.height())

    def __layout(self):
        self.vLayout = QVBoxLayout()
        self.vLayout.addWidget(self.label_about)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vLayout)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
