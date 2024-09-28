import socket
from random import random, randrange, randint

def send_udp_packet(destination_ip='127.0.0.1', destination_port=33203, message='Hello, UDP!'):
    # Создаем UDP сокет
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Отправляем сообщение
        udp_socket.sendto(message.encode('utf-8'), (destination_ip, destination_port))
        print(f"Пакет отправлен на {destination_ip}:{destination_port} с сообщением: '{message}'")
    except Exception as e:
        print(f"Ошибка при отправке пакета: {e}")
    finally:
        # Закрываем сокет
        udp_socket.close()

if __name__ == "__main__":
    lol = randint(0, 11111111)
    send_udp_packet(message=f"Hello, UDP. {lol}")
