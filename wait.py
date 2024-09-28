import sys
import socket
import random
from PyQt5 import QtWidgets, QtGui, QtCore

class NetworkDataReceiver(QtCore.QThread):
    data_received = QtCore.pyqtSignal(str, str, str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.running = True

    def run(self):
        while self.running:
            data, address = self.socket.recvfrom(1024)
            sender_ip, sender_port = address
            decoded_data = data.decode('utf-8')
            self.data_received.emit(sender_ip, str(sender_port), decoded_data)

    def stop(self):
        self.running = False
        self.socket.close()

class CardDisplay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 400)  # Фиксированный размер контейнера для карточек
        self.cards = []  # Список для хранения карточек
        self.setStyleSheet("background-color: #2c3e50;")

    def add_card(self, ip, port, data):
        card = DraggableCard(ip, port, data)
        card.setParent(self)  # Устанавливаем родительский виджет
        card.show()  # Отображаем карточку
        self.cards.append(card)  # Добавляем карточку в список

        # Генерация случайного положения карточки в пределах окна
        max_x = self.width() - card.width()
        max_y = self.height() - card.height()
        random_x = random.randint(0, max_x)
        random_y = random.randint(0, max_y)
        
        card.move(random_x, random_y)  # Перемещение карточки в случайное место
        card.raise_()  # Перемещаем карточку на передний план

class DraggableCard(QtWidgets.QGroupBox):
    def __init__(self, ip, port, data):
        super().__init__(f"Sender: {ip}:{port}")
        self.ip = ip
        self.port = port
        self.data = data
        self.setFixedSize(200, 100)  # Фиксированный размер карточки

        # Задание случайного цвета для фона карточки
        random_color = self.generate_random_color()
        self.setStyleSheet(f"""
            background-color: {random_color};
            border: 2px solid #1abc9c;
            border-radius: 10px;
        """)
        self.init_ui()

        self.start_pos = None
        self.is_dragging = False

    def init_ui(self):
        card_layout = QtWidgets.QVBoxLayout()
        card_layout.addWidget(QtWidgets.QLabel(f"Data: {self.data}"))
        self.setLayout(card_layout)

        self.mousePressEvent = self.mouse_press_event
        self.mouseMoveEvent = self.mouse_move_event
        self.mouseReleaseEvent = self.mouse_release_event
        self.mouseDoubleClickEvent = self.mouse_double_click_event

    def generate_random_color(self):
        """Генерация случайного цвета в формате RGB."""
        r = random.randint(50, 100)  # Ограничиваем диапазон, чтобы цвет не был слишком ярким или темным
        g = random.randint(50, 100)
        b = random.randint(50, 100)
        return f'rgb({r}, {g}, {b})'

    def mouse_press_event(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = event.pos()
            self.is_dragging = True
            self.raise_()  # Перемещаем карточку на передний план

    def mouse_move_event(self, event):
        if self.is_dragging:
            self.move(self.pos() + event.pos() - self.start_pos)

    def mouse_release_event(self, event):
        self.is_dragging = False
        self.start_pos = None

    def mouse_double_click_event(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.show_data()

    def show_data(self):
        detail_window = DataDetailWindow(self.data)
        detail_window.exec_()

class DataDetailWindow(QtWidgets.QDialog):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Card Data Details")
        self.setFixedSize(300, 200)
        self.init_ui(data)

    def init_ui(self, data):
        layout = QtWidgets.QVBoxLayout()
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(data)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

class MainApplication(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.card_display = CardDisplay()
        self.network_receiver = NetworkDataReceiver(port=33203)
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle("Network Data Receiver")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("""
            background-color: #2c3e50;
            color: #ecf0f1;
            font-family: 'Arial';
            font-size: 14px;
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.card_display)
        self.setLayout(layout)

        self.fade_in_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.fade_in_animation.setDuration(1000)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.start()

    def setup_connections(self):
        self.network_receiver.data_received.connect(self.card_display.add_card)
        self.network_receiver.start()  # Запускаем поток для прослушивания данных

    def closeEvent(self, event):
        self.network_receiver.stop()  # Остановка потока при закрытии окна
        event.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_application = MainApplication()
    main_application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
