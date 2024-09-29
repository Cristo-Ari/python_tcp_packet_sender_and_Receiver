import sys
import socket
import random
from PyQt5 import QtWidgets, QtGui, QtCore

class NetworkDataReceiver(QtCore.QThread):
    data_received_signal = QtCore.pyqtSignal(str, str, str)

    def __init__(self, port_number):
        super().__init__()
        self.port_number = port_number
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('0.0.0.0', self.port_number))
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                data_packet, address = self.udp_socket.recvfrom(1024)
                sender_ip, sender_port = address
                decoded_data = data_packet.decode('utf-8')
                self.data_received_signal.emit(sender_ip, str(sender_port), decoded_data)
            except OSError as e:
                if str(e) == "[WinError 10038] An operation was attempted on something that is not a socket":
                    break  # Прерываем цикл, если сокет закрыт
                else:
                    print(f"Error occurred: {e}")

    def stop(self):
        self.is_running = False
        self.udp_socket.close()
        self.wait()  # Ждем, пока поток завершится

class CardDisplay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 800)
        self.cards = []
        self.setStyleSheet("background-color: #34495e;")
        self.layout = QtWidgets.QVBoxLayout(self)

        self.delete_button = QtWidgets.QPushButton("Удалить карточки", self)
        self.delete_button.setFixedSize(150, 50)  # Прямоугольная форма с соотношением сторон 1:2
        self.delete_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgb(255, 0, 0),  /* Красный */
                    stop: 1 rgb(255, 182, 193)  /* Розовый */
                );
                color: white;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgb(220, 0, 0),  /* Темно-красный при наведении */
                    stop: 1 rgb(255, 105, 180)  /* Ярко-розовый при наведении */
                );
            }
        """)
        self.delete_button.clicked.connect(self.remove_all_cards)
        self.layout.addWidget(self.delete_button, alignment=QtCore.Qt.AlignTop)

    def add_card(self, ip_address, port_number, message_data):
        card = DraggableCard(ip_address, port_number, message_data)
        card.setParent(self)
        card.show()

        x_position = random.randint(0, self.width() - card.width())
        y_position = random.randint(0, self.height() - card.height())
        card.move(x_position, y_position)
        self.cards.append(card)
        card.raise_()

    def remove_all_cards(self):
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()

class DraggableCard(QtWidgets.QGroupBox):
    def __init__(self, ip_address, port_number, message_data):
        super().__init__(f"Sender: {ip_address}:{port_number}")
        self.setFixedSize(400, 200)
        self.data = message_data

        self.setStyleSheet(self.generate_gradient_style())
        self.init_ui()
        
        self.is_dragging = False

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        text_container = QtWidgets.QTextEdit(self)
        text_container.setReadOnly(True)
        
        text_container.setPlainText(self.data)

        text_container.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)  
        text_container.setMinimumSize(380, 180)
        text_container.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        text_container.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)  

        layout.addWidget(text_container)
        self.setLayout(layout)

    def generate_gradient_style(self):
        gradient_colors = [
            (random.randint(100, 180), random.randint(100, 180), random.randint(100, 180)),
            (random.randint(50, 100), random.randint(50, 100), random.randint(50, 100))
        ]
        gradient_style = f"""
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgb({gradient_colors[0][0]}, {gradient_colors[0][1]}, {gradient_colors[0][2]}),
                stop: 1 rgb({gradient_colors[1][0]}, {gradient_colors[1][1]}, {gradient_colors[1][2]})
            );
            border: 2px solid #1abc9c;
            border-radius: 10px;
            padding: 5px;
        """
        return gradient_style

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.pos()
            self.raise_()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(self.pos() + event.pos() - self.drag_start_position)

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            detail_window = DataDetailWindow(self.data)
            detail_window.exec_()

class DataDetailWindow(QtWidgets.QDialog):
    def __init__(self, message_data):
        super().__init__()
        self.setWindowTitle("Data Details")
        self.setFixedSize(300, 200)
        layout = QtWidgets.QVBoxLayout()

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(message_data)
        self.text_edit.setStyleSheet(""" 
            font-family: 'Open Sans', sans-serif;
            font-size: 13px;
            color: #34495e;
            background-color: #ecf0f1;
        """)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

class MainApplication(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.card_display = CardDisplay()
        self.network_receiver = NetworkDataReceiver(port_number=33203)
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle("Network Data Receiver")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            background-color: #34495e;
            color: #ecf0f1;
            font-family: 'Arial', sans-serif;
            font-size: 14px;
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.card_display)
        self.setLayout(layout)

        self.fade_in_animation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        self.fade_in_animation.setDuration(800)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.start()

    def setup_connections(self):
        self.network_receiver.data_received_signal.connect(self.card_display.add_card)
        self.network_receiver.start()

    def closeEvent(self, event):
        self.network_receiver.stop()  # Остановка сетевого потока
        event.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_application = MainApplication()
    main_application.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
