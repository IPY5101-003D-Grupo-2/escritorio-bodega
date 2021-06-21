import requests
import sys
from PyQt5.QtWidgets import QAbstractScrollArea, QDialog, QFormLayout, QLabel, QLineEdit, QMainWindow, QMessageBox, QApplication, QPushButton, QStyledItemDelegate, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import urllib
# datos_tabla = "url;nombre;tipo;sku;precio;caracteristicas;modelo;modo_operacion;alimentacion_electrica;consumo_electrico;capacidad_nominal;caudal_aire;nivel_ruido;dimensiones;peso_neto;modelo_kit_cañerias;conexion_cañerias;ficha;imagen; stock"
datos_tabla = "SKU;NOMBRE;TIPO;CANTIDAD PROVEEDOR;CANTIDAD BODEGA;ACCION"
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
        outerLayout = QVBoxLayout()
        tablelayout = QVBoxLayout()
        tablelayout.addWidget(self.tableWidget)
        outerLayout.addLayout(self.form)
        outerLayout.addLayout(tablelayout)
        self.setLayout(outerLayout)
        self.show()

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(len(lista_headers))
        self.tableWidget.setHorizontalHeaderLabels(
            (lista_headers))
        self.tableWidget.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)
        delegate = ReadOnlyDelegate(self.tableWidget)
        self.tableWidget.setItemDelegate(delegate)
        self.tableWidget.move(0, 0)

        self.tableWidget.doubleClicked.connect(self.on_click)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

    def createForm(self):
        self.nameLineEdit = QLineEdit()
        self.form = QFormLayout()
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

    def cambiar_stock(self, sku, cantidad):
        url = 'https://ws-buenos-aires.herokuapp.com/inventario/modificar-cantidad/'

        print(sku, cantidad)
        data = {
            "SKU": str(sku),
            "CANTIDAD": int(cantidad)
        }
        response = requests.post(url, json=data)
        print(response.text)
        if response.status_code == 200:
            titulo = "REALIZADO"
            texto = "REALIZADO CON EXITO"
        else:
            titulo = "ERROR"
            texto = "NO PUDO SER REALIZADO"
        self.traer_todos_los_productos()
        dlg = QMessageBox(self)
        dlg.setWindowTitle(titulo)
        dlg.setText(texto)
        dlg.exec()

    def on_click_open_modal(self):
        combo = self.sender()
        index = self.tableWidget.indexAt(combo.pos())
        sku = self.tableWidget.item(index.row(), 0).text()
        dialog = QDialog()
        dialog.setWindowTitle(f"Cambiar stock de {sku}")
        e1 = QLineEdit()
        dialog_form = QFormLayout(dialog)
        e1.setValidator(QIntValidator())
        e1.setMaxLength(4)
        e1.setAlignment(Qt.AlignRight)

        dialog_form.addRow(QLabel("Cantidad a modificar"), e1)
        button1 = QPushButton("CAMBIAR STOCK")

        button1.clicked.connect(
            lambda: self.cambiar_stock(sku, int(e1.text())))

        dialog_form.addRow("", button1)

        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def traer_todos_los_productos(self, sku=None):
        index = 0
        if sku is not None:
            response = requests.get(
                f'https://ws-buenos-aires.herokuapp.com/inventario-proveedor/?sku={sku}')
        else:
            response = requests.get(
                'https://ws-buenos-aires.herokuapp.com/inventario-proveedor/')
        productos = response.json()
        self.tableWidget.setRowCount(len(productos))

        for producto in productos:
            self.tableWidget.setItem(index, lista_headers.index("SKU"), QTableWidgetItem(producto.get(
                "SKU")))
            self.tableWidget.setItem(index, lista_headers.index("NOMBRE"), QTableWidgetItem(producto.get(
                "NOMBRE")))
            self.tableWidget.setItem(index, lista_headers.index("TIPO"), QTableWidgetItem(producto.get(
                "TIPO")))
            self.tableWidget.setItem(index, lista_headers.index("CANTIDAD PROVEEDOR"), QTableWidgetItem(str(producto.get(
                "CANTIDADPROVEEDOR"))))
            self.tableWidget.setItem(index, lista_headers.index("CANTIDAD BODEGA"), QTableWidgetItem(str(producto.get(
                "CANTIDADINVENTARIO"))))
            btn = QPushButton("MODIFICAR CANTIDAD", self)
            btn.clicked.connect(self.on_click_open_modal)
            self.tableWidget.setCellWidget(
                index, lista_headers.index("ACCION"), btn)
            index += 1
        self.tableWidget.resizeColumnsToContents()

    def onClicked(self):
        self.tableWidget.setRowCount(0)
        sku = self.nameLineEdit.text()
        if sku == "":
            self.traer_todos_los_productos()
        else:
            self.traer_todos_los_productos(sku=sku)

        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
