import socket as Socket
import sys
from common import *

# Endereço IP padrão do servidor
server_address = ('localhost', 51511)

# ID do servidor que intermediará a comunicação
server_id = sys.argv[1]
# ID do exibidor associado é passado via linha de comando para o emissor
associated_exhibitor_id = sys.argv[2] 

# Create a TCP/IP socket
socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)

# Abre a conexão com o servidor
socket.connect(server_address)
print(f'Emissor inicializado em {server_address[0]}:{server_address[1]}')

# Abertura do processo de comunicação pelo envio da mensagem HI(3) e leitura do ID designado
# à esse emissor pelo servidor.
id = send_hi_message(socket, associated_exhibitor_id, server_id, 2)

while(True):
    # Realiza a leitura de mensagens do terminal
    raw_message = input().split(" ")

    if(raw_message[0] == "kill"):
        send_kill_message(socket, id, server_id, 9999)
        break
    elif(raw_message[0] == "origin"):
        send_origin_message(socket, id, server_id, 9999, raw_message[1], raw_message[2])
    elif(raw_message[0] == "msg"):
        _, destination_id, msg_size, msg = raw_message
        send_msg_message(socket, id, destination_id, 9999, msg_size, msg)
    elif(raw_message[0] == "creq"):
        _, destination_id = raw_message
        send_creq_message(socket, id, destination_id, 9999)
    elif(raw_message[0] == "planet"):
        _, client_id = raw_message
        send_msg_message(socket, id, client_id, 9999)
    elif(raw_message[0] == "planetlist"): 
        _, exhibitor_id = raw_message
        send_msg_message(socket, id, exhibitor_id, 9999)
    else:
        send_kill_message(socket, id, server_id, 9999)
        break

print(f'closing socket {socket.getsockname()}')
socket.close()


