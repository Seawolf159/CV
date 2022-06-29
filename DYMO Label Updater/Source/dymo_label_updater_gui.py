import os

import darkdetect
import qdarktheme
from PyQt5 import QtCore, QtWidgets

import dymo_label_updater as dlu
from dymo_label_updater_ui import Ui_MainWindow

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ui = Ui_MainWindow()
        self.ui = ui

        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.change_excel)
        self.ui.textBrowser.setMarkdown(dlu.load_setting("path", "excel"))
        self.ui.textBrowser.mouseDoubleClickEvent = self.open_excel

        self.ui.pushButton_2.clicked.connect(self.change_label_location)
        self.ui.textBrowser_2.setMarkdown(
            dlu.load_setting("path", "label_location")
        )
        self.ui.textBrowser_2.mouseDoubleClickEvent = self.open_label_location

        self.ui.pushButton_3.clicked.connect(self.select_short_template)
        self.ui.textBrowser_3.setMarkdown(
            dlu.load_setting("path", "short_template")
        )
        self.ui.textBrowser_3.mouseDoubleClickEvent = self.open_short_template

        self.ui.pushButton_4.clicked.connect(self.select_long_template)
        self.ui.textBrowser_4.setMarkdown(
            dlu.load_setting("path", "long_template")
        )
        self.ui.textBrowser_4.mouseDoubleClickEvent = self.open_long_template

        self.ui.pushButton_5.clicked.connect(self.select_settings)
        self.ui.textBrowser_5.setMarkdown(
            dlu.load_setting("path", "settings")
        )
        self.ui.textBrowser_5.mouseDoubleClickEvent = self.open_settings

        self.ui.pushButton_6.clicked.connect(self.make_labels)

    def change_excel(self):
        chosen_file = self.select_file("*.xlsx")[0]
        if not chosen_file:
            return

        dlu.save_setting("path", "excel", chosen_file)
        self.ui.textBrowser.setMarkdown(chosen_file)

    def select_file(self, extension):
        chosen_file = QtWidgets.QFileDialog.getOpenFileName(filter=extension)
        if chosen_file:
            return chosen_file

    def open_excel(self, _):
        directory = dlu.load_setting("path", "excel")
        os.startfile(directory)

    def change_label_location(self):
        chosen_directory = self.select_directory()
        if not chosen_directory:
            return

        dlu.save_setting("path", "label_location", chosen_directory)
        self.ui.textBrowser_2.setMarkdown(chosen_directory)

    def select_directory(self):
        chosen_directory = QtWidgets.QFileDialog.getExistingDirectory()
        if chosen_directory:
            return chosen_directory

    def open_label_location(self, _):
        directory = dlu.load_setting("path", "label_location")
        os.startfile(directory)

    def select_short_template(self):
        chosen_file = self.select_file("*.label")[0]
        if not chosen_file:
            return

        dlu.save_setting("path", "short_template", chosen_file)
        self.ui.textBrowser_3.setMarkdown(chosen_file)

    def open_short_template(self, _):
        directory = dlu.load_setting("path", "short_template")
        os.startfile(directory)

    def select_long_template(self):
        chosen_file = self.select_file("*.label")[0]
        if not chosen_file:
            return

        dlu.save_setting("path", "long_template", chosen_file)
        self.ui.textBrowser_4.setMarkdown(chosen_file)

    def open_long_template(self, _):
        directory = dlu.load_setting("path", "long_template")
        os.startfile(directory)

    def select_settings(self):
        chosen_file = self.select_file("*.ini")[0]
        if not chosen_file:
            return

        dlu.save_setting("path", "settings", chosen_file)
        self.ui.textBrowser_5.setMarkdown(chosen_file)

    def open_settings(self, _):
        directory = dlu.load_setting("path", "settings")
        os.startfile(directory)

    def make_labels(self):
        # Step 2: Create a QThread object
        self.thread = QtCore.QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.ui.pushButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_2.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_5.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.progressBar.setValue(0)
        )

    def update_progress(self, value):
        self.ui.progressBar.setValue(value)


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def run(self):
        dlu.create_and_save_labels(self.progress)
        self.finished.emit()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    if darkdetect.isDark():
        app.setStyleSheet(qdarktheme.load_stylesheet())
    else:
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
