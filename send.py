import sys
import socket
import random
import re
from PyQt5 import QtWidgets, QtCore


class UdpPacketSenderApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("UDP Packet Sender")
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: #34495e; color: #ecf0f1; font-family: 'Arial';")

        self.layout = QtWidgets.QHBoxLayout()

        self.status_area_scroll_area = QtWidgets.QScrollArea()
        self.status_area_scroll_area.setWidgetResizable(True)
        self.status_area_scroll_area.setFixedWidth(700)

        self.status_area_widget = QtWidgets.QWidget()
        self.status_area_layout = QtWidgets.QVBoxLayout(self.status_area_widget)
        self.status_area_layout.setAlignment(QtCore.Qt.AlignTop)
        self.status_area_scroll_area.setWidget(self.status_area_widget)
        self.layout.addWidget(self.status_area_scroll_area)

        self.message_area_layout = QtWidgets.QVBoxLayout()

        self.destination_ip_label = QtWidgets.QLabel("Destination IP:")
        self.destination_ip_input = QtWidgets.QLineEdit("localhost")
        self.destination_ip_input.setStyleSheet("font-size: 14px;")

        self.destination_port_label = QtWidgets.QLabel("Destination Port:")
        self.destination_port_input = QtWidgets.QLineEdit("33203")
        self.destination_port_input.setStyleSheet("font-size: 14px;")

        self.message_label = QtWidgets.QLabel("Message:")
        self.message_input = QtWidgets.QTextEdit()
        self.message_input.setPlainText("Hello, UDP! {random number 200 1000000}")
        self.message_input.setStyleSheet("font-size: 14px; background-color: #ecf0f1; color: #34495e;")

        self.send_button = QtWidgets.QPushButton("Send UDP Packet")
        self.send_button.setStyleSheet(""" 
            QPushButton {
                background-color: #1abc9c;
                color: white;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        self.send_button.clicked.connect(self.send_udp_packet)

        self.message_area_layout.addWidget(self.destination_ip_label)
        self.message_area_layout.addWidget(self.destination_ip_input)
        self.message_area_layout.addWidget(self.destination_port_label)
        self.message_area_layout.addWidget(self.destination_port_input)
        self.message_area_layout.addWidget(self.message_label)
        self.message_area_layout.addWidget(self.message_input)
        self.message_area_layout.addWidget(self.send_button)

        self.layout.addLayout(self.message_area_layout)
        self.setLayout(self.layout)

    def send_udp_packet(self):
        destination_ip = self.destination_ip_input.text()
        destination_port = int(self.destination_port_input.text())
        message = self.message_input.toPlainText().strip()

        message_with_random_numbers = self.replace_random_number_placeholders(message)

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            udp_socket.sendto(message_with_random_numbers.encode('utf-8'), (destination_ip, destination_port))
            self.add_status_card("Success", f"Packet sent to {destination_ip}:{destination_port} with message: '{message_with_random_numbers}'")
        except Exception as e:
            self.add_status_card("Error", f"Failed to send packet: {e}")
        finally:
            udp_socket.close()

    def replace_random_number_placeholders(self, message):
        def random_number_replacer(match):
            min_value = int(match.group(1))
            max_value = int(match.group(2))
            return str(random.randint(min_value, max_value))

        pattern = r'\{random number (\d+) (\d+)\}'
        return re.sub(pattern, random_number_replacer, message)

    def add_status_card(self, title, message):
        card_background_color = self.generate_random_dark_color()
        lighter_background_color = self.lighten_color(card_background_color, 30)

        card = QtWidgets.QGroupBox(title)
        card.setFixedWidth(650)
        card.setStyleSheet(f"""
            QGroupBox {{
                background-color: {card_background_color};
                border: 1px solid #3498db;
                border-radius: 8px;
                margin: 5px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px; 
                padding: 5px;
                color: white;
                font-size: 12px;
            }}
        """)

        layout = QtWidgets.QVBoxLayout()

        message_label = QtWidgets.QLabel(message)
        message_label.setStyleSheet(f"""
            color: white; 
            font-size: 12px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {card_background_color}, stop:1 {lighter_background_color});  
            border-radius: 4px;
            padding: 5px;
        """)
        
        message_label.setWordWrap(True)  
        message_label.setMinimumHeight(20)  

        layout.addWidget(message_label)  

        card.setLayout(layout)

        self.status_area_layout.addWidget(card)

        QtCore.QTimer.singleShot(1, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        self.status_area_scroll_area.verticalScrollBar().setValue(self.status_area_scroll_area.verticalScrollBar().maximum())

    def generate_random_dark_color(self):
        red_value = random.randint(0, 127)
        green_value = random.randint(0, 127)
        blue_value = random.randint(0, 127)
        return f"rgb({red_value}, {green_value}, {blue_value})"

    def lighten_color(self, color, amount):
        rgb_values = [int(c) for c in color[4:-1].split(",")]
        lighter_rgb_values = [min(255, c + amount) for c in rgb_values]
        return f"rgb({lighter_rgb_values[0]}, {lighter_rgb_values[1]}, {lighter_rgb_values[2]})"

def main():
    app = QtWidgets.QApplication(sys.argv)
    udp_sender_app = UdpPacketSenderApp()
    udp_sender_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
