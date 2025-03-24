import socket

# Configuração do cliente
HOST = 'server'  # Nome do serviço do container servidor ou IP
PORT = 5555      # Mesma porta do servidor

# Criação do socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Loop para enviar mensagens
while True:
    message = input("Digite uma mensagem (ou 'sair' para encerrar): ")
    client_socket.send(message.encode())
    
    if message.lower() == 'sair':
        break

# Fecha a conexão
client_socket.close()