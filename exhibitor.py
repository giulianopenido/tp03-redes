import sys
import socket as Socket
from common import *

# Endereço IP padrão do servidor
server_address = ('localhost', 51511)

# ID do servidor que intermediará a comunicação
server_id = sys.argv[1]

# Create a TCP/IP socket
socket = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
print(f'connecting to {server_address[0]} port {server_address[1]}')
socket.connect(server_address)

id = send_hi_message(socket, 0, server_id, 1)

command_type, planet_name_size, planet_name = input().split(" ")
if(command_type != "origin"):
    raise Exception("Exibidor sem um planeta associado")
else:
    send_origin_message(socket, id, server_id, 9999, planet_name_size, planet_name)

while(True):
    # Send messages on both sockets
    message_type, emitter_id, destination_id, remaining_data = decode_header( socket.recv(BUFFER_SIZE).decode("utf-8") )


    if(destination_id != id or destination_id != 0):
        raise Exception("Mensagem entregue ao exibidor errado!")

    if(message_type == message_type_to_int_code["msg"]):
        message = remaining_data[-1]
        print(f"msg de {emitter_id}: \"{message}\"")
    elif(message_type == message_type_to_int_code["clist"]):
        clist = remaining_data[-1]
        print(f"clist: \"{clist}\"")
    elif(message_type == message_type_to_int_code["planet"]):
        planet_name = remaining_data[-1]
        print(f"planet of {destination_id}: {planet_name}")
    elif(message_type == message_type_to_int_code["planetlist"]):
        planet_list = remaining_data[-1]
        print(f"planetlist: {planet_list}")
    elif(message_type == message_type_to_int_code["kill"]):
        send_ok_message(socket, id, server_id, 9999)
        break;

socket.close()