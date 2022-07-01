import os
import sys

import darkdetect
import qdarktheme
from PyQt5 import QtCore, QtWidgets

import wo_filer as wf
from wo_filer_ui import Ui_MainWindow

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        ui = Ui_MainWindow()
        self.ui = ui

        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.save_one)

        self.ui.pushButton_2.clicked.connect(self.save_more)

        self.ui.pushButton_3.clicked.connect(self.change_save_location)

        store_location = wf.retrieve_setting("path", "store_location")
        self.ui.textBrowser.setMarkdown(store_location)
        self.ui.textBrowser.mouseDoubleClickEvent = self.open_store_location

        self.ui.pushButton_4.clicked.connect(self.change_setting_location)

        store_location = wf.retrieve_setting("path", "setting_location")
        self.ui.textBrowser_2.setMarkdown(store_location)
        self.ui.textBrowser_2.mouseDoubleClickEvent = self.open_setting_location

    def save_one(self):
        chosen_file = self.select_pdf()[0]
        if not chosen_file:
            return

        # Step 2: Create a QThread object
        self.thread = QtCore.QThread()
        # Step 3: Create a worker object
        self.worker = WorkerOne()
        self.worker.chosen_file = chosen_file
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
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.ui.pushButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_2.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_3.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_4.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.progressBar.setValue(0)
        )

    def update_progress(self, value):
        self.ui.progressBar.setValue(value)

    def select_pdf(self):
        chosen_file = QtWidgets.QFileDialog.getOpenFileName(filter="*.pdf")
        if chosen_file:
            return chosen_file

    def save_more(self):
        chosen_directory = self.select_directory()
        if not chosen_directory:
            return

        # Step 2: Create a QThread object
        self.thread = QtCore.QThread()
        # Step 3: Create a worker object
        self.worker = WorkerTwo()
        self.worker.chosen_directory = chosen_directory
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
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.ui.pushButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_2.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_3.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.pushButton_4.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.ui.progressBar.setValue(0)
        )

    def change_save_location(self):
        chosen_directory = self.select_directory()
        if not chosen_directory:
            return

        wf.store_setting("path", "store_location", chosen_directory)
        self.ui.textBrowser.setMarkdown(chosen_directory)

    def open_store_location(self, _):
        store_location = wf.retrieve_setting("path", "store_location")
        os.startfile(store_location)

    def change_setting_location(self):
        chosen_file = self.select_file("*.ini")[0]
        if not chosen_file:
            return

        wf.store_setting("path", "setting_location", chosen_file)
        self.ui.textBrowser_2.setMarkdown(chosen_file)

    def select_file(self, extension):
        chosen_file = QtWidgets.QFileDialog.getOpenFileName(filter=extension)
        if chosen_file:
            return chosen_file

    def open_setting_location(self, _):
        directory = wf.retrieve_setting("path", "setting_location")
        os.startfile(directory)

    def select_directory(self):
        chosen_directory = QtWidgets.QFileDialog.getExistingDirectory()
        if chosen_directory:
            return chosen_directory


class WorkerOne(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    chosen_file = ""

    def run(self):
        wf.save_one(self.chosen_file, self.progress)
        self.finished.emit()


class WorkerTwo(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    chosen_directory = ""

    def run(self):
        wf.save_more(self.chosen_directory, self.progress)
        self.finished.emit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    if darkdetect.isDark():
        app.setStyleSheet(qdarktheme.load_stylesheet())
    else:
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
