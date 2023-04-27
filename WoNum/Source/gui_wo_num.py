import os
import sys
import traceback

import qdarktheme
from PySide6 import QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTreeWidgetItem,
    QTreeWidgetItemIterator,
)

import wo_num
from ui_wo_num import Ui_MainWindow

sys.argv += ["-platform", "windows:darkmode=2"]
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_forms()
        self.ui.treeWidget.itemChanged.connect(self.check_box_pressed)
        self.ui.treeWidget.itemPressed.connect(self.check_box_label_pressed)
        self.ui.pushButton.clicked.connect(self.hard_print_selected_items)

        icon = QIcon()
        icon_path = wo_num.FROZEN_DIR.joinpath("Resources/icon.ico").as_posix()
        icon.addFile(icon_path, QtCore.QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

        # flags
        self.flag_uncheck_parent = False
        self.flag_skip_item_changed_function = False

    def load_forms(self):
        dir_num = 0
        for dir in wo_num.FORMS_PATH.glob("*"):
            # Do not include empty directories nor files.
            try:
                if not any(dir.iterdir()):
                    continue
            except NotADirectoryError:
                continue

            dir_name = dir.name.lower().capitalize()
            # Do not include temp direcory:
            if dir_name == wo_num.TEMP_PATH.name.lower().capitalize():
                continue

            tree = self.ui.treeWidget

            top_level = QTreeWidgetItem(tree)
            top_level.setFlags(
                QtCore.Qt.ItemIsSelectable
                | QtCore.Qt.ItemIsUserCheckable
                | QtCore.Qt.ItemIsEnabled
            )
            top_level.setCheckState(0, QtCore.Qt.Unchecked)

            top_level = tree.topLevelItem(dir_num)
            top_level.setText(0, dir_name)
            dir_num += 1

            for form_num, form in enumerate(dir.glob("*.docx")):
                filename = form.name
                child = QTreeWidgetItem(top_level)
                child.setFlags(
                    QtCore.Qt.ItemIsSelectable
                    | QtCore.Qt.ItemIsUserCheckable
                    | QtCore.Qt.ItemIsEnabled
                )
                child.setCheckState(0, QtCore.Qt.Unchecked)

                child = top_level.child(form_num)
                child.setText(0, filename)

    def check_box_pressed(self, item, column):
        if self.flag_skip_item_changed_function:
            return
        tree = item.treeWidget()
        state = item.checkState(column)
        checked = QtCore.Qt.CheckState.Checked
        unchecked = QtCore.Qt.CheckState.Unchecked
        if item.parent():
            parent = item.parent()
        else:
            parent = item

        if item is parent and state == checked:
            if not item.isExpanded():
                item.setExpanded(True)
                self.flag_skip_item_changed_function = True
                item.setCheckState(column, unchecked)
                self.flag_skip_item_changed_function = False
                return

            self.set_all_boxes_in_parent(tree, column, parent, checked)
            self.flag_uncheck_parent = False

        elif item is parent and state == unchecked:
            if not item.isExpanded():
                item.setExpanded(True)
                self.flag_skip_item_changed_function = True
                item.setCheckState(column, checked)
                self.flag_skip_item_changed_function = False
                return

            if not self.flag_uncheck_parent:
                self.set_all_boxes_in_parent(tree, column, parent, unchecked)
            self.flag_uncheck_parent = False

        # Uncheck the parent check box when any other check box is unchecked in
        # that column.
        elif state == unchecked:
            self.flag_uncheck_parent = True
            parent.setCheckState(column, unchecked)

    @staticmethod
    def set_all_boxes_in_parent(tree, column, parent, state):
        iterator = QTreeWidgetItemIterator(tree)
        while iterator.value():
            item = iterator.value()
            if item.parent() is parent:
                item.setCheckState(column, state)
            iterator += 1

    def check_box_label_pressed(self, item, column):
        tree = item.treeWidget()
        state = item.checkState(column)
        checked = QtCore.Qt.CheckState.Checked
        unchecked = QtCore.Qt.CheckState.Unchecked
        if item.parent():
            parent = item.parent()
        else:
            parent = item

        if item is parent and state == unchecked:
            if not item.isExpanded():
                item.setExpanded(True)
                return

            self.flag_skip_item_changed_function = True
            self.set_all_boxes_in_parent(tree, column, parent, checked)
            self.flag_uncheck_parent = False

        elif item is parent and state == checked:
            if not item.isExpanded():
                item.setExpanded(True)
                return

            if not self.flag_uncheck_parent:
                self.flag_skip_item_changed_function = True
                self.set_all_boxes_in_parent(tree, column, parent, unchecked)
            self.flag_uncheck_parent = False

        # Uncheck the parent check box when any other check box is unchecked in
        # that column.
        elif state == checked:
            self.flag_uncheck_parent = True
            parent.setCheckState(column, unchecked)

        if state == unchecked:
            item.setCheckState(column, checked)
        else:
            item.setCheckState(column, unchecked)

        self.flag_skip_item_changed_function = False

    def hard_print_selected_items(self):
        iterator = QTreeWidgetItemIterator(self.ui.treeWidget)
        checked = QtCore.Qt.CheckState.Checked

        checked_items = []
        while iterator.value():
            item = iterator.value()
            if item.parent():
                if item.checkState(0) == checked:
                    category = item.parent().text(0).lower()
                    checked_items.append([category, item.text(0)])

            iterator += 1

        if not checked_items:
            self.display_error("You haven't selected anything!")
            return

        hard_print_amount = self.hard_print_amount()

        # Create a QThread object
        self.thread = QtCore.QThread()

        # Create a worker object
        self.worker = Worker(checked_items, hard_print_amount)

        # Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.error.connect(self.display_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        # Start the thread
        self.thread.start()

        # Final resets
        self.ui.pushButton.setEnabled(False)
        self.ui.spinBox.setValue(1)
        self.worker.finished.connect(lambda: self.ui.progressBar.setValue(0))
        self.worker.finished.connect(
            lambda: self.ui.pushButton.setEnabled(True)
        )

    def hard_print_amount(self):
        return self.ui.spinBox.value()

    def display_error(self, error):
        QMessageBox.warning(self, "Whoopsie!", error)

    def update_progress(self, value):
        self.ui.progressBar.setValue(value)


class Worker(QtCore.QObject):
    finished = QtCore.Signal()
    error = QtCore.Signal(str)
    progress = QtCore.Signal(int)
    backend = wo_num.WoNum()

    def __init__(self, checked_items, hard_print_amount):
        super().__init__()
        self.checked_items = checked_items
        self.hard_print_amount = hard_print_amount

    def run(self):
        try:
            self.backend.main(
                self.checked_items, self.progress, self.hard_print_amount
            )
        except Exception:
            self.error.emit(traceback.format_exc())

        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
