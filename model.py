# -*- coding: utf-8 -*-
""" @author: Gabriel Maccari """

import pandas
import numpy
import matplotlib
import matplotlib.pyplot as plt
from csv import Sniffer
from windrose import WindroseAxes

from view_controller import show_selection_dialog, show_wait_cursor

matplotlib.use("svg")

X_LABELS = {
    4: ['E', 'N', 'W', 'S'],
    8: ['E', '', 'N', '', 'W', '', 'S', ''],
    16: ['E', '', '', '', 'N', '', '', '', 'W', '', '', '', 'S', '', '', '']
}


class Model:
    def __init__(self):
        self.df = None

    def read_file(self, path: str):
        show_wait_cursor()

        # Arquivo csv
        if path.endswith(".csv"):
            sniffer = Sniffer()
            data = open(path, "r").read(4096)
            sep = str(sniffer.sniff(data).delimiter)
            decimal = '.'  # if sep == ',' else ','
            df = pandas.read_csv(path, delimiter=sep, decimal=decimal)

        # Arquivo xlsx, xlsm ou ods
        else:
            engine = ("odf" if path.endswith(".ods") else "openpyxl")
            excel_file = pandas.ExcelFile(path, engine=engine)
            sheets = excel_file.sheet_names
            # Se houver mais de 1 aba, o usuário seleciona uma delas
            if len(sheets) > 1:
                show_wait_cursor(False)
                sheet, ok = show_selection_dialog("Selecione a aba desejada:", sheets)
                show_wait_cursor()
                if not ok:
                    show_wait_cursor(False)
                    return False
            else:
                sheet = 0
            df = excel_file.parse(sheet_name=sheet)
            # Converte os nomes das colunas para string
            df.columns = df.columns.astype(str)
            # Descarta colunas sem nome
            df = df.drop([col for col in df.columns if 'Unnamed' in col], axis='columns')
            # Descarta linhas vazias
            df = df.dropna(how='all', axis='index')
            # Verifica se existem linhas preenchidas no arquivo
            if len(df.index) <= 0:
                raise IndexError('A tabela selecionada está vazia ou contém apenas cabeçalhos.')

        show_wait_cursor(False)

        # Checa se o dataframe foi criado ou não
        if isinstance(df, pandas.DataFrame):
            self.df = df.copy()
            return True
        else:
            return False

    def check_column(self, selected_column: str, col: int = 1):
        df = self.df
        try:
            df[selected_column] = df[selected_column].replace(",", ".", regex=True)
            df[selected_column] = df[selected_column].astype("float64")

            if col == 1:
                if not df[selected_column].dropna().between(0, 360).all():
                    return False

            self.df[selected_column] = df[selected_column]
            return True
        except ValueError:
            return False

    def get_column2_min_max_values(self, column2: str):
        values = self.df[column2].dropna().values
        min_val = min(values)
        max_val = max(values)
        return min_val, max_val

    def plot_windrose(self, column1: str, column2: str = None, show_x_axis: bool = True, show_y_axis: bool = True,
                      show_x_labels: bool = True, show_y_labels: bool = True, y_labels_position: float = 56.25,
                      mirror_bars: bool = False, n_sectors: int = 16, title: str = "", show_legend: bool = False,
                      legend_title: str = "Valor", bar_divisions: int = 6, column2_bounds: list | tuple = (0, 9999),
                      bar_color: str = "#000000", colormap: str = "viridis_r") -> matplotlib.pyplot.Figure:
        """
        Plota um diagrama de roseta com os parâmetros dados.
        :param column1: Coluna dos dados de direção.
        :param column2: Coluna dos dados de intensidade, se houver.
        :param show_x_axis: Mostrar ou não as linhas do eixo X.
        :param show_y_axis: Mostrar ou não as linhas do eixo Y.
        :param show_x_labels: Mostrar ou não os rótulos do eixo X.
        :param show_y_labels: Mostrar ou não os rótulos do eixo Y.
        :param y_labels_position: Posição angular dos rótulos de Y.
        :param mirror_bars: Espelhar ou não os dados.
        :param n_sectors: Número de direções do diagrama.
        :param title: Título do diagrama.
        :param show_legend: Mostrar ou não a legenda dos dados de intensidade.
        :param legend_title: Título da legenda.
        :param bar_divisions: Número de divisões das barras em relação aos dados de intensidade.
        :param column2_bounds: Mínimo e máximo dos dados de intensidade.
        :param bar_color: Cor das barras (quando a intensidade não é plotada).
        :param colormap: Rampa de cores de intensidade.
        :return: A figura com o diagrama plotado.
        """
        values1 = self.df[column1]

        x_labels = X_LABELS[n_sectors]
        if not show_x_labels:
            for i, item in enumerate(x_labels):
                x_labels[i] = ""

        # Calcula os setores e o ângulo de início com base no número de sentidos
        sector_width = 360 / n_sectors
        start_angle = (sector_width / 2) * (-1)

        # Divisões das barras
        if column2 is not None:
            values2 = self.df[column2]
            min_val, max_val = column2_bounds[0], column2_bounds[1]
            divisions = numpy.arange(min_val, max_val, (max_val/bar_divisions))
        else:
            values2 = [1 for x, val in enumerate(values1)]
            divisions = numpy.arange(0, 1, 1)

        # Espelha os dados
        if mirror_bars:
            mirrored_values = []
            for v in values1:
                mirrored_values.append(v + 180 if v < 180 else v - 180)
            values1_mirror = numpy.array(mirrored_values)
            values1 = numpy.concatenate((values1, values1_mirror))
            values2 = numpy.concatenate((values2, values2))

        # Por causa de algum bug estranho, se você plota um histograma aleatório antes de plotar o diagrama de roseta,
        # ele arredonda os finais das barras e fica mais bonito
        plt.hist([0, 1])

        # Cria a figura
        fig = plt.figure(figsize=(6, 6), dpi=600)
        ax = fig.add_subplot(111, projection="windrose")

        if column2 is not None:
            ax.bar(
                values1, values2, normed=False, nsector=n_sectors, opening=1, cmap=matplotlib.colormaps[colormap],
                edgecolor='white', linewidth=0.7, bins=divisions
            )
            if show_legend:
                ax.set_legend(title=legend_title, loc="lower right")
        else:
            ax.bar(
                values1, values2, normed=False, nsector=n_sectors, opening=1, colors=bar_color, edgecolor='white',
                linewidth=0.7, bins=divisions
            )

        # Ajusta o diagrama
        ax.set_thetagrids(numpy.arange(0, 360, sector_width), labels=x_labels)
        ax.set_facecolor('white')
        ax.set_rlabel_position(y_labels_position)
        if not show_y_labels:
            ax.yaxis.set_ticklabels([])
        if title != "":
            ax.set_title(title, y=1.07, fontsize=18, fontweight='bold')
        ax.yaxis.grid(show_y_axis)
        ax.xaxis.grid(show_x_axis)

        return fig
