import socket as Socket
import sys
from common import *

# Endereço IP padrão do servidor
server_address = ('localhost', 51511)

# ID do servidor que intermediará a comunicação
server_id = sys.argv[1]
# ID do exibidor associado é passado via linha de comando para o emissor
associated_exhibitor_id = sys.argv[2] 

# Criação do socket TCP/IP
socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)

# Abre a conexão com o servidor
socket.connect(server_address)

# Abertura do processo de comunicação pelo envio da mensagem HI(3) e leitura do ID designado
# à esse emissor pelo servidor.
id = send_hi_message(socket, associated_exhibitor_id, server_id, 2)

# Variável que armazena o sequence de mensagens desse cliente
sequence = 0

while(True):
    # Realiza a leitura de mensagens do terminal
    raw_message = input("> ").split(" ")

    if(raw_message[0] == "kill"):
        send_kill_message(socket, id, server_id, sequence)
        sequence+=1
        break
    elif(raw_message[0] == "origin"):
        send_origin_message(socket, id, server_id, sequence, raw_message[1], raw_message[2])
        sequence+=1
    elif(raw_message[0] == "msg"):
        _, destination_id, msg_size = raw_message[:3]
        msg = " ".join(raw_message[3:])
        send_msg_message(socket, id, destination_id, sequence, msg_size, msg)
    elif(raw_message[0] == "creq"):
        _, destination_id = raw_message
        send_creq_message(socket, id, destination_id, sequence)
        sequence+=1
    elif(raw_message[0] == "planet"):
        _, client_id = raw_message
        send_planet_message(socket, id, client_id, sequence)
    elif(raw_message[0] == "planetlist"): 
        send_planetlist_message(socket, id, server_id, sequence, wait_for_ok_answer=True)
    else:
        send_kill_message(socket, id, server_id, sequence)
        break

print(f'Encerrando o socket...')
socket.close()


