import requests
import sys
from PyQt5.QtWidgets import QAbstractScrollArea, QDialog, QFormLayout, QLabel, QLineEdit, QMainWindow, QApplication, QPushButton, QStyledItemDelegate, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import urllib
# datos_tabla = "url;nombre;tipo;sku;precio;caracteristicas;modelo;modo_operacion;alimentacion_electrica;consumo_electrico;capacidad_nominal;caudal_aire;nivel_ruido;dimensiones;peso_neto;modelo_kit_cañerias;conexion_cañerias;ficha;imagen; stock"
datos_tabla = "sku;nombre;tipo;stock;accion"
lista_headers = datos_tabla.split(";")


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index) -> QWidget:
        return


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'APP BODEGA'
        self.left = 0
        self.top = 0
        self.width = 1000
        self.height = 700
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createForm()
        self.createTable()
        # Add box layout, add table to box layout and add box layout to widget
        outerLayout = QVBoxLayout()

        tablelayout = QVBoxLayout()
        tablelayout.addWidget(self.tableWidget)
        outerLayout.addLayout(self.form)
        outerLayout.addLayout(tablelayout)
        self.setLayout(outerLayout)

        # Show widget
        self.show()

    def createTable(self):
       # Create table
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(len(lista_headers))
        self.tableWidget.setHorizontalHeaderLabels(
            (lista_headers))
        self.tableWidget.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)
        # self.tableWidget.setItem(0, 0, QTableWidgetItem("Cell (1,1)"))
        # self.tableWidget.setItem(0, 1, QTableWidgetItem("Cell (1,2)"))
        # self.tableWidget.setItem(1, 0, QTableWidgetItem("Cell (2,1)"))
        # self.tableWidget.setItem(1, 1, QTableWidgetItem("Cell (2,2)"))
        # self.tableWidget.setItem(2, 0, QTableWidgetItem("Cell (3,1)"))
        # self.tableWidget.setItem(2, 1, QTableWidgetItem("Cell (3,2)"))
        # self.tableWidget.setItem(3, 0, QTableWidgetItem("Cell (4,1)"))
        # self.tableWidget.setItem(3, 1, QTableWidgetItem("Cell (4,2)"))

        delegate = ReadOnlyDelegate(self.tableWidget)
        self.tableWidget.setItemDelegate(delegate)
        self.tableWidget.move(0, 0)

        self.tableWidget.doubleClicked.connect(self.on_click)
        # Table will fit the screen horizontally
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

    def createForm(self):
        self.nameLineEdit = QLineEdit()
        # creating a form layout
        self.form = QFormLayout()
        # adding rows
        # for name and adding input text
        self.form.addRow(QLabel("SKU"), self.nameLineEdit)

        self.button1 = QPushButton("BUSCAR", self)
        self.button1.clicked.connect(self.onClicked)

        self.form.addRow(self.button1)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(),
                  currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    def on_click_open_modal(self):
        combo = self.sender()
        index = self.tableWidget.indexAt(combo.pos())
        sku = self.tableWidget.item(index.row(), 0).text()
        dialog = QDialog()
        # dialog.ui = Ui_MyDialog()
        # dialog.ui.setupUi(dialog)
        dialog.setWindowTitle(f"Cambiar stock de {sku}")
        e1 = QLineEdit()
        dialog_form = QFormLayout(dialog)
        e1.setValidator(QIntValidator())
        e1.setMaxLength(4)
        e1.setAlignment(Qt.AlignRight)

        dialog_form.addRow(QLabel("Cantidad a modificar"), e1)
        button1 = QPushButton("CAMBIAR STOCK")
        dialog_form.addRow("", button1)

        dialog.setWindowModality(Qt.ApplicationModal)
        # dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.exec_()

    def onClicked(self):
        self.tableWidget.setRowCount(0)
        sku = self.nameLineEdit.text()
        print(sku)
        index = 0
        if sku == "":
            response = requests.get(
                'https://anwo-web-service.herokuapp.com/api/productos/all')
            productos = response.json().get("productos")
            self.tableWidget.setRowCount(len(productos))

            for producto in productos:
                self.tableWidget.setItem(index, lista_headers.index("sku"), QTableWidgetItem(producto.get(
                    "sku")))
                self.tableWidget.setItem(index, lista_headers.index("nombre"), QTableWidgetItem(producto.get(
                    "nombre")))
                self.tableWidget.setItem(index, lista_headers.index("tipo"), QTableWidgetItem(producto.get(
                    "tipo")))
                self.tableWidget.setItem(index, lista_headers.index("stock"), QTableWidgetItem(str(producto.get(
                    "stock"))))
                btn = QPushButton("BUSCAR", self)
                btn.clicked.connect(self.on_click_open_modal)
                self.tableWidget.setCellWidget(
                    index, lista_headers.index("accion"), btn)

                # img_url = urllib.request.urlopen(producto.get(
                #     "imagen")).read()
                # img = QImage()
                # img.loadFromData(img_url)
                # pic = QPixmap(img)
                # img_final = QLabel(self)
                # img_final.setMinimumWidth(200)
                # img_final.setMinimumHeight(200)

                # img_final.setPixmap(pic)
                # self.tableWidget.setCellWidget(
                #     index, lista_headers.index("imagen"), img_final)
                index += 1
            self.tableWidget.resizeColumnsToContents()

        else:
            response = requests.get(
                f"https://anwo-web-service.herokuapp.com/api/productos/sku/{sku}")
            producto = response.json()
            if not producto.get("error"):
                producto = producto.get("doc")
                self.tableWidget.setRowCount(1)
                self.tableWidget.setItem(index, lista_headers.index("sku"), QTableWidgetItem(producto.get(
                    "sku")))
                self.tableWidget.setItem(index, lista_headers.index("nombre"), QTableWidgetItem(producto.get(
                    "nombre")))
                self.tableWidget.setItem(index, lista_headers.index("tipo"), QTableWidgetItem(producto.get(
                    "tipo")))
                self.tableWidget.setItem(index, lista_headers.index("stock"), QTableWidgetItem(str(producto.get(
                    "stock"))))

        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
