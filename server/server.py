import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

def handle_client(conn, addr):
    print(f"Conectado por {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Mensagem de {addr}: {data.decode()}")
    conn.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)  # Aumentado para suportar mais conexões

print("Servidor aguardando conexões...")
while True:
    conn, addr = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()