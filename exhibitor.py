import sys
import socket as Socket
from common import *

# Endereço IP padrão do servidor
server_address = ('localhost', 51511)

# ID do servidor que intermediará a comunicação
server_id = sys.argv[1]

# Criação do socket TCP/IP
socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)

# Abre a conexão com o servidor
socket.connect(server_address)

# Variável que armazena o sequence de mensagens desse cliente
sequence = 0

# Abertura do processo de comunicação pelo envio da mensagem HI(3) e leitura do ID designado
# à esse emissor pelo servidor.
id = send_hi_message(socket, 0, server_id, sequence)
sequence+=1

# Lê o planeta do exibidor antes de começar a escutar mensagens enviadas pelo servidor
command_type, planet_name_size, planet_name = input("> ").split(" ")
if(command_type != "origin"):
    raise Exception("Exibidor sem um planeta associado")
else:
    send_origin_message(socket, id, server_id, sequence, planet_name_size, planet_name)
    sequence+=1

#Loop de leitura de mensagens
while(True):
    raw_message = decode_message( socket.recv(BUFFER_SIZE) ) # Leitura da mensagem e transformação do formato de dados
    message_type, emitter_id, destination_id, sequence = raw_message[:4]

    if(message_type == message_type_to_int_code["msg"]):
        message = raw_message[-1]
        sequence = raw_message[3]
        print(f"< msg de {emitter_id}: \"{message}\"")
    elif(message_type == message_type_to_int_code["clist"]):
        clist = raw_message[-1]
        print(f"< clist: {clist}")
    elif(message_type == message_type_to_int_code["planet"]):
        planet_name = raw_message[-1]
        sequence = raw_message[3]
        print(f"< planet of {destination_id}: {planet_name}")
    elif(message_type == message_type_to_int_code["planetlist"]):
        planet_list = raw_message[-1]
        sequence = raw_message[3]
        print(f"< planetlist: {planet_list}")
    elif(message_type == message_type_to_int_code["kill"]):
        print("< kill")
        send_ok_message(socket, id, server_id, sequence)
        break
socket.close()