from http import client
from common import *
import select
import socket as Socket

# ID do servidor
id = 2**16 - 1

# Classe responsável por gerenciar as conexões e o recebimento de mensagens
class Connection_manager():

    def __init__(self):

        self.inputs = []
        # Dicionário que armazena os dados dos clientes conectados
        # [id] : {planeta, socket e cliente_associado}
        self.emitters = {}
        self.exhibitors = {} 

        # Lista de IDs disponíveis para cada tipo de cliente
        self.available_emitter_ids = list(range(1, 2**12))
        self.available_exhibitor_ids = list(range(2**12, 2**13)) 

    # Função que verifica se determinado cliente é um emissor
    def isEmitter(self, id):
        return id >= 1 and id < 2**12

    # Gera uma lista com o ID de todos os clientes conectados
    def get_client_list(self):
        return [client for client in list(self.emitters.keys()) + list(self.exhibitors.keys())]

    # Gera uma lista com o nome de todos os planetas que possuem um cliente ativo
    def get_planet_list(self):
        planet_set = set()
        all_clients =  {**self.emitters, **self.exhibitors}
        for client_id in all_clients:
            planet = all_clients[client_id]["planet"]
            if(planet):
                planet_set.add(planet)
        return list(planet_set)

    #Função que lida com as mensagens recebidas e delega o processamento de acordo com o tipo
    def handle_message(self, source_socket, encoded_message):
        message = decode_message(encoded_message)
        message_type = message[0]
        if(message_type == message_type_to_int_code["hi"]):
            self.handle_hi_message(source_socket, message)
        elif(message_type == message_type_to_int_code["origin"]):
            self.handle_origin_message(source_socket, message)
        elif(message_type == message_type_to_int_code["msg"]):
            self.handle_msg_message(source_socket, message, encoded_message)
        elif(message_type == message_type_to_int_code["ok"]):
            print(f'< ok from {message[1]}')
        elif(message_type == message_type_to_int_code["creq"]):
            self.handle_creq_message(source_socket, message)
        elif(message_type == message_type_to_int_code["planet"]):
            self.handle_planet_message(source_socket, message)
        elif(message_type == message_type_to_int_code["planetlist"]):
            self.handle_planetlist_message(source_socket, message)
        elif(message_type == message_type_to_int_code["kill"]):
            self.handle_kill_message(source_socket, message)


    def handle_hi_message(self, source_socket, message):
        print("Mensagem hi recebida")
        _, source_id, _, sequence = message
        new_id = 0
        if(source_id == 0): # Cliente é um exibidor
            new_id = self.available_exhibitor_ids.pop(0)
            self.exhibitors[new_id] = {
                "socket": source_socket, "emitter": None, "planet": None, "current_sequence": 1
            }
        else: # Cliente é um emissor
            new_id = self.available_emitter_ids.pop(0)
            associated_exhibitor = source_id if source_id in self.exhibitors else None
            self.emitters[new_id] = {
                "socket": source_socket, "exhibitor": associated_exhibitor,
                "planet": None, "current_sequence": 1
            }
        send_ok_message(source_socket, id, new_id, sequence, f"ok {new_id}")

    def handle_origin_message(self, source_socket, message):
        _, source_id, _, _, sequence, planet_name = message
        if(self.isEmitter(source_id)):
            self.emitters[source_id]["planet"] = planet_name
        else:
            self.exhibitors[source_id]["planet"] = planet_name
        print(f"Recebido {planet_name} de {source_id}")
        send_ok_message(source_socket, id, source_id, sequence)

    def handle_msg_message(self, source_socket, message, encoded_message):
        _, _, destination_id, _, _, _ = message


        if(destination_id == 0): #broadcast
            for exhibitor_id in self.exhibitors:
                self.exhibitors[exhibitor_id]["socket"].send(encoded_message)
        else:
            self.exhibitors[destination_id]["socket"].send(encoded_message)

    def handle_creq_message(self, source_socket, message):
        _, source_id, destination_id, sequence = message

        destination_socket = self.exhibitors[destination_id]["socket"]

        try:
            send_clist_message(destination_socket, source_id, destination_id, sequence, self.get_client_list())
        except:
            pass
        send_ok_message(source_socket, id, source_id, sequence) 

    def handle_planet_message(self, source_socket, message):
        _, source_id, client_id, sequence = message
        exhibitor_id = 0
        planet_name = ""
        if(client_id in self.emitters):
            exhibitor_id = self.emitters[client_id]["exhibitor"]
            planet_name = self.emitters[client_id]["planet"]
        else:
            exhibitor_id = client_id
            planet_name = self.exhibitors[client_id]["planet"]
        destination_socket = self.exhibitors[exhibitor_id]["socket"]
        planet_name = planet_name if(planet_name) else "Não informado!"
        send_ok_message(source_socket, id, source_id, sequence) 
        send_planet_message(destination_socket, source_id, client_id, sequence, planet_name)

    def handle_planetlist_message(self, source_socket, message):
        _, source_id, _,  sequence = message
        planet_list = self.get_planet_list()
        associated_exhibitor_id = self.emitters[source_id]["exhibitor"]

        if(not associated_exhibitor_id or associated_exhibitor_id not in self.exhibitors):
            send_error_message(source_socket, id, source_id, sequence)
            return
        exhibitor_socket = self.exhibitors[associated_exhibitor_id]["socket"]
        send_planetlist_message(exhibitor_socket, source_id, associated_exhibitor_id, sequence, planet_list=planet_list)

        send_ok_message(source_socket, id, source_id, sequence)

    def handle_kill_message(self, source_socket, message):
        _, source_id, _,  sequence = message
        print(f"Recebido kill de {source_id}")

        associated_exhibitor_id = self.emitters[source_id]["exhibitor"]
        associated_exhibitor_socket = self.exhibitors[associated_exhibitor_id]["socket"]

        self.inputs.remove(source_socket)
        self.inputs.remove(associated_exhibitor_socket)
        self.available_emitter_ids.append(source_id)
        self.available_exhibitor_ids.append(associated_exhibitor_id)

        send_ok_message(source_socket, id, source_id, sequence)
        send_kill_message(associated_exhibitor_socket, id, associated_exhibitor_id, sequence)

listener = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
listener.setsockopt(Socket.SOL_SOCKET, Socket.SO_REUSEADDR, 1)
listener.setblocking(0)

server_address = ('localhost', 51511)

listener.bind(server_address)
print(f'Servidor inicializado em {server_address[0]}:{server_address[1]} - ID: {id}')

listener.listen(5)

connection_manager = Connection_manager()
connection_manager.inputs = [ listener ]


while(True):
    readable, _, _ = select.select(connection_manager.inputs, [], connection_manager.inputs)
    for socket in readable:
        if socket is listener:
            connection, client_address = socket.accept()
            connection.setblocking(0)
            connection_manager.inputs.append(connection)

        else:
            raw_data = socket.recv(BUFFER_SIZE)
            if raw_data:
                connection_manager.handle_message(socket, raw_data)
            


