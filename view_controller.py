# -*- coding: utf-8 -*-
""" @author: Gabriel Maccari """

import os
import matplotlib
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from icecream import ic

matplotlib.use("svg")

SECTORS = {
    "Cardeais, colaterais e subcolaterais": 16,
    "Cardeais e colaterais": 8,
    "Cardeais": 4
}


class ViewController(QMainWindow):
    column1_ok = True
    column2_ok = True
    plot_window = None

    def __init__(self, model):
        self.model = model
        super().__init__()

        self.setWindowTitle("Rose Charter")
        self.setWindowIcon(QIcon("icons/window_icon.ico"))

        y = 5
        self.file_label = QLabel("Selecione um arquivo para começar.", self)
        self.file_label.setGeometry(5, y, 240, 20)

        self.open_file_button = QToolButton(self)
        self.open_file_button.setText("Selecionar")
        self.open_file_button.setGeometry(245, y, 80, 20)
        self.open_file_button.clicked.connect(self.open_file_button_pressed)

        y += 25
        self.divider = QFrame(self)
        self.divider.setGeometry(5, y, 320, 3)
        self.divider.setLineWidth(1)
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setFrameShadow(QFrame.Shadow.Sunken)

        y += 10
        self.column1_label = QLabel("Dados para comprimento dos leques (Ex: direção):", self)
        self.column1_label.setGeometry(5, y, 320, 18)
        self.column1_label.setEnabled(False)

        y += 18
        self.column1_combo = QComboBox(self)
        self.column1_combo.setGeometry(5, y, 297, 20)
        self.column1_combo.setEnabled(False)
        self.column1_combo.currentTextChanged.connect(lambda: self.column_selected(1))

        self.column1_icon = QPushButton(self)
        self.column1_icon.setGeometry(305, y, 20, 20)
        self.column1_icon.setIcon(QIcon("icons/circle.png"))
        self.column1_icon.setFlat(True)

        y += 30
        self.column2_checkbox = QCheckBox("Dados para divisão dos leques (Ex: velocidade):", self)
        self.column2_checkbox.setGeometry(5, y, 320, 18)
        self.column2_checkbox.clicked.connect(self.enable_column2_combo)
        self.column2_checkbox.setEnabled(False)

        y += 18
        self.column2_combo = QComboBox(self)
        self.column2_combo.setGeometry(5, y, 297, 20)
        self.column2_combo.setEnabled(False)
        self.column2_combo.currentTextChanged.connect(lambda: self.column_selected(2))

        self.column2_icon = QPushButton(self)
        self.column2_icon.setGeometry(305, y, 20, 20)
        self.column2_icon.setIcon(QIcon("icons/circle.png"))
        self.column2_icon.setFlat(True)

        y += 30
        self.mirror_checkbox = QCheckBox("Espelhar dados", self)
        self.mirror_checkbox.setGeometry(5, y, 160, 20)
        self.mirror_checkbox.setToolTip("Ao selecionar esta opção, sentidos opostos serão somados e espelhados.")

        self.y_axis_checkbox = QCheckBox("Mostrar eixo Y (circular)", self)
        self.y_axis_checkbox.setGeometry(160, y, 160, 20)
        self.y_axis_checkbox.setChecked(True)

        y += 20
        self.x_axis_checkbox = QCheckBox("Mostrar eixo X (radial)", self)
        self.x_axis_checkbox.setGeometry(5, y, 160, 20)
        self.x_axis_checkbox.setChecked(True)

        self.y_labels_checkbox = QCheckBox("Mostrar rótulos de Y", self)
        self.y_labels_checkbox.setGeometry(160, y, 160, 20)
        self.y_labels_checkbox.setChecked(True)

        y += 20
        self.x_labels_checkbox = QCheckBox("Mostrar rótulos de X", self)
        self.x_labels_checkbox.setGeometry(5, y, 160, 20)
        self.x_labels_checkbox.setChecked(True)

        self.color_label = QLabel("Cor dos leques:", self)
        self.color_label.setGeometry(160, y, 150, 20)

        self.color_button = QPushButton("#000000", self)
        self.color_button.setGeometry(245, y, 55, 20)
        self.color_button.clicked.connect(self.color_button_pressed)

        y += 25
        self.y_labels_position_label = QLabel("Posição dos rótulos de Y (°):", self)
        self.y_labels_position_label.setGeometry(5, y, 150, 20)

        self.y_labels_position_spinbox = QDoubleSpinBox(self)
        self.y_labels_position_spinbox.setGeometry(155, y, 55, 20)
        self.y_labels_position_spinbox.setRange(0, 360)
        self.y_labels_position_spinbox.setValue(56.25)

        y += 25
        self.sectors_combo_label = QLabel("Setores do diagrama:", self)
        self.sectors_combo_label.setGeometry(5, y, 160, 18)

        y += 18
        self.sectors_combo = QComboBox(self)
        self.sectors_combo.setGeometry(5, y, 320, 20)
        self.sectors_combo.addItems(["Cardeais, colaterais e subcolaterais", "Cardeais e colaterais", "Cardeais"])

        y += 25
        self.title_edit_label = QLabel("Título do gráfico:", self)
        self.title_edit_label.setGeometry(5, y, 115, 18)

        y += 18
        self.title_edit = QLineEdit("", self)
        self.title_edit.setGeometry(5, y, 320, 20)

        y += 30
        self.legend_checkbox = QCheckBox("Legenda:", self)
        self.legend_checkbox.setGeometry(5, y, 320, 18)
        self.legend_checkbox.clicked.connect(self.legend_checkbox_clicked)
        self.legend_checkbox.setEnabled(False)

        y += 18
        self.legend_title_edit = QLineEdit("Mergulho", self)
        self.legend_title_edit.setGeometry(5, y, 320, 20)
        self.legend_title_edit.setEnabled(False)

        y += 25
        self.column2_divisions_label = QLabel("Divisões de leque:", self)
        self.column2_divisions_label.setGeometry(5, y, 95, 20)
        self.column2_divisions_label.setEnabled(False)

        self.column2_divisions_spinbox = QSpinBox(self)
        self.column2_divisions_spinbox.setValue(6)
        self.column2_divisions_spinbox.setGeometry(105, y, 35, 20)
        self.column2_divisions_spinbox.setEnabled(False)

        self.column2_interval_label = QLabel("Intervalo:", self)
        self.column2_interval_label.setGeometry(145, y, 60, 20)
        self.column2_interval_label.setEnabled(False)

        self.column2_min_edit = QDoubleSpinBox(self)
        self.column2_min_edit.setValue(0)
        self.column2_min_edit.setDecimals(1)
        self.column2_min_edit.setRange(0, 99999)
        self.column2_min_edit.setGeometry(200, y, 55, 20)
        self.column2_min_edit.setEnabled(False)

        self.column2_interval_sep = QLabel("-", self)
        self.column2_interval_sep.setGeometry(255, y, 15, 20)
        self.column2_interval_sep.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.column2_max_edit = QDoubleSpinBox(self)
        self.column2_max_edit.setValue(90)
        self.column2_max_edit.setDecimals(1)
        self.column2_max_edit.setRange(0, 99999)
        self.column2_max_edit.setGeometry(270, y, 55, 20)
        self.column2_max_edit.setEnabled(False)

        y += 30
        self.plot_diagram_button = QToolButton(self)
        self.plot_diagram_button.setText('Plotar diagrama')
        self.plot_diagram_button.setGeometry(5, y, 320, 30)
        self.plot_diagram_button.setEnabled(False)
        self.plot_diagram_button.clicked.connect(self.plot_diagram_button_pressed)

        y += 35
        self.setMinimumSize(330, y)
        self.setMaximumSize(330, y)

    def open_file_button_pressed(self):
        try:
            new_file_opened = False

            path = show_file_dialog(
                "Selecione uma tabela contendo os dados de entrada.",
                "Formatos suportados (*.xlsx *.xlsm *.csv *.ods);;",
                mode="open"
            )
            if path == "":
                return

            show_wait_cursor()

            new_file_opened = self.model.read_file(path)

            if new_file_opened:
                self.column1_label.setEnabled(True)
                self.column1_combo.setEnabled(True)
                self.column2_checkbox.setEnabled(True)
                columns = self.model.df.columns.to_list()
                self.fill_column_combos(columns)
                file_name = path.split("/")
                self.file_label.setText(file_name[-1])

            show_wait_cursor(False)

        except Exception as exception:
            handle_exception(exception, "open_file_button_pressed")

    def fill_column_combos(self, columns):
        self.column1_combo.disconnect()
        self.column1_combo.clear()
        self.column1_combo.currentTextChanged.connect(lambda: self.column_selected(1))
        self.column1_combo.addItems(columns)

        self.column2_combo.disconnect()
        self.column2_combo.clear()
        self.column2_combo.currentTextChanged.connect(lambda: self.column_selected(2))
        self.column2_combo.addItems(columns)

    def column_selected(self, col: int):
        try:
            combobox = self.column1_combo if col == 1 else self.column2_combo
            selected_col = combobox.currentText()
            valid_col = self.model.check_column(selected_col, col)

            if col == 1:
                self.column1_ok = valid_col
                val = self.column1_ok
            else:
                if self.column2_checkbox.isChecked():
                    self.column2_ok = valid_col
                else:
                    self.column2_ok = True
                val = self.column2_ok

            check_button = self.column1_icon if col == 1 else self.column2_icon
            icon = "icons/ok.png" if val else "icons/not_ok.png"
            check_button.setIcon(QIcon(icon))
            if val:
                tooltip = "OK"
            elif not val and col == 1:
                tooltip = "A coluna deve conter apenas dados numéricos entre 0 e 360"
            else:
                tooltip = "A coluna deve conter apenas dados numéricos"
            check_button.setToolTip(tooltip)

            if valid_col and col == 2:
                min_val, max_val = self.model.get_column2_min_max_values(selected_col)
                self.column2_min_edit.setValue(min_val)
                self.column2_max_edit.setValue(max_val)

            self.plot_diagram_button.setEnabled(self.column1_ok and self.column2_ok)
        except Exception as exception:
            handle_exception(exception, "column_selected")

    def enable_column2_combo(self):
        try:
            enabled = self.column2_checkbox.isChecked()
            self.column2_combo.setEnabled(enabled)
            self.column_selected(2)

            color = "#000000" if not enabled else "magma_r"
            self.color_button.setText(color)
            self.color_button.setStyleSheet(f"color: {color}")
            self.color_button.setFixedWidth(55 if not enabled else 80)
            self.color_button.disconnect()
            function = self.color_button_pressed if not enabled else self.colormap_button_pressed
            self.color_button.clicked.connect(function)

            self.legend_checkbox.setEnabled(enabled)
            if not enabled:
                self.legend_checkbox.setChecked(False)

            self.column2_divisions_label.setEnabled(enabled)
            self.column2_divisions_spinbox.setEnabled(enabled)
            self.column2_interval_label.setEnabled(enabled)
            self.column2_min_edit.setEnabled(enabled)
            self.column2_max_edit.setEnabled(enabled)

        except Exception as exception:
            handle_exception(exception, "enable_column2_combo")

    def color_button_pressed(self):
        try:
            color = QColorDialog.getColor()
            color = color.name()
            self.color_button.setStyleSheet(f"color: {color}")
            self.color_button.setText(color)
        except Exception as exception:
            handle_exception(exception, "color_button_pressed")

    def colormap_button_pressed(self):
        try:
            colormaps = sorted(matplotlib.colormaps())
            colormap, ok = show_selection_dialog("Selecione o esquema de cores:", colormaps)
            if ok:
                self.color_button.setText(colormap)
        except Exception as exception:
            handle_exception(exception, "colormap_button_pressed")

    def legend_checkbox_clicked(self):
        try:
            show_legend = self.legend_checkbox.isChecked()
            self.legend_title_edit.setEnabled(show_legend)
        except Exception as exception:
            handle_exception(exception, "legend_checkbox_clicked")

    def plot_diagram_button_pressed(self):
        try:
            show_wait_cursor()

            column1 = self.column1_combo.currentText()
            column2 = self.column2_combo.currentText() if self.column2_checkbox.isChecked() else None
            show_x_axis = self.x_axis_checkbox.isChecked()
            show_x_labels = self.x_labels_checkbox.isChecked()
            show_y_axis = self.y_axis_checkbox.isChecked()
            show_y_labels = self.y_labels_checkbox.isChecked()
            mirror_bars = self.mirror_checkbox.isChecked()
            y_labels_position = 90 - self.y_labels_position_spinbox.value()
            n_sectors = SECTORS[self.sectors_combo.currentText()]
            title = self.title_edit.text()
            show_legend = self.legend_checkbox.isChecked()
            legend_title = self.legend_title_edit.text()
            bar_divisions = self.column2_divisions_spinbox.value()
            column2_bounds = (self.column2_min_edit.value(), self.column2_max_edit.value())
            bar_color = self.color_button.text() if not column2 else None
            colormap = self.color_button.text() if column2 else None

            matplotlib.pyplot.clf()
            fig = self.model.plot_windrose(
                column1, column2, show_x_axis, show_y_axis, show_x_labels, show_y_labels, y_labels_position,
                mirror_bars, n_sectors, title, show_legend, legend_title, bar_divisions, column2_bounds, bar_color,
                colormap
            )

            try:
                self.plot_window.close()
            except (UnboundLocalError, AttributeError):
                pass

            self.plot_window = PlotWindow(self, fig)

            show_wait_cursor(False)

            self.plot_window.show()
        except Exception as exception:
            handle_exception(exception, "plot_diagram_button_pressed")


class PlotWindow(QMainWindow):
    def __init__(self, parent, fig):
        super(PlotWindow, self).__init__(parent)

        self.parent = parent
        self.fig = fig

        self.setWindowTitle("Diagrama")
        self.setWindowIcon(QIcon('icons/window_icon.ico'))
        self.setFixedSize(425, 425)

        img = self.get_plot_img()

        self.plot_canvas = QPushButton(self)
        self.plot_canvas.setIcon(QIcon(img))
        self.plot_canvas.setIconSize(QSize(415, 415))
        self.plot_canvas.setFlat(True)
        self.plot_canvas.setGeometry(5, 5, 415, 415)

        self.save_button = QPushButton(self)
        self.save_button.setIcon(QIcon('icons/save.png'))
        self.save_button.setIconSize(QSize(26, 26))
        self.save_button.setGeometry(5, 5, 30, 30)
        self.save_button.clicked.connect(self.save_plot)

        self.path_label = QLabel(img, self)
        self.path_label.setStyleSheet("font-size: 7pt; color: gray")
        self.path_label.setGeometry(5, 405, 400, 15)

    def get_plot_img(self):
        try:
            plot_folder = f"{os.getcwd()}\\plots"
            if not os.path.exists(plot_folder):
                os.makedirs(plot_folder)

            i = 0
            while True:
                fig_name = f"{plot_folder}\\plot{i}.png"
                if not os.path.exists(fig_name):
                    break
                i += 1

            matplotlib.pyplot.savefig(fig_name, dpi=300, transparent=True, format='png')
            return fig_name
        except Exception as exception:
            handle_exception(exception, "get_plot_img")
            self.close()

    def save_plot(self):
        try:
            output_file = show_file_dialog(
                "Salvar diagrama de roseta",
                "PNG (*.png);;JPEG (*.jpg);; SVG (*.svg)",
                "save"
            )
            if output_file != "":
                output_format = output_file[-3:]
                self.fig.savefig(output_file, dpi=600, transparent=True, format=output_format)
                show_popup("Arquivo salvo com sucesso!", parent=self)
        except Exception as exception:
            handle_exception(exception, "save_plot")


def show_file_dialog(caption: str, extension_filter: str, mode: str = "open", parent: QMainWindow = None):
    dialog = QFileDialog(parent)
    if mode == "open":
        file_name, file_type = dialog.getOpenFileName(caption=caption, filter=extension_filter, parent=parent)
    else:
        file_name, file_type = dialog.getSaveFileName(caption=caption, filter=extension_filter, parent=parent)
    return file_name


def show_selection_dialog(message: str, items: list, selected: int = 0, title: str = "Selecionar opções",
                          parent: QMainWindow = None) -> (str, bool):
    dialog = QInputDialog(parent)
    choice, ok = dialog.getItem(parent, title, message, items, selected, editable=False)
    return choice, ok


def show_wait_cursor(activate: bool = True):
    if activate:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    else:
        QApplication.restoreOverrideCursor()


def show_popup(message, msg_type="notification", parent: QMainWindow = None):
    popup_types = {
        "notification": {"title": "Notificação", "icon": "icons/info.png"},
        "error":        {"title": "Erro",        "icon": "icons/error.png"}
    }
    title = popup_types[msg_type]["title"]
    icon = QIcon(popup_types[msg_type]["icon"])

    popup = QMessageBox(parent)
    popup.setText(message)
    popup.setWindowTitle(title)
    popup.setWindowIcon(icon)
    popup.exec()


def handle_exception(exception: Exception, context: str):
    ic(exception, context)
    show_wait_cursor(False)
    show_popup(f"ERRO: {exception}\nCONTEXTO: {context}", msg_type="error")
