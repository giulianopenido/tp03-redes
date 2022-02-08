from common import *
import select
import socket
import queue

class Connection_manager():

    def __init__(self):
        self.emitters = {}
        self.exhibitors = {} 
        self.available_emitter_ids = list(range(1, 2**12))
        self.available_exhibitor_ids = list(range(2**12, 2**13)) 

    def handle_message(self, source_socket, encoded_message):
        message = decode_message(encoded_message)
        message_type = message[0]
        if(message_type == message_type_to_int_code("hi")):
            print("Mensagem hi recebida")
            self.handle_hi_message(source_socket, message)
        elif(message_type == message_type_to_int_code("origin")):
            print("")


    def handle_hi_message(self, source_socket, message):
        _, source_id, destination_id, _ = message
        if(source_id == 0): # Cliente é um exibidor
            new_id = self.available_exhibitor_ids.pop(0)
            associated_emitter = destination_id if destination_id in self.exhibitors else None
            self.exhibitors[new_id] = [source_socket, associated_emitter]



id = 2**16 - 1

# Create a TCP/IP socket
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 51511)

listener.bind(server_address)
print(f'Servidor inicializado em {server_address[0]}:{server_address[1]} - ID: {id}')

# Listen for incoming connections
listener.listen(5)

# Sockets from which we expect to read
inputs = [ listener ]

# Sockets to which we expect to write
outputs = [ ]

message_queues = {}


while(True):
    readable, _, _ = select.select(inputs, outputs, inputs)
    for s in readable:
        if s is listener:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print(f'new connection from {client_address}')
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = queue.Queue()
        else:
            data = s.recv(BUFFER_SIZE).decode("utf-8")
            if data:
                # A readable client socket has data
                print(f'received {type(data)} from {s.getpeername()}')
                message_queues[s].put(data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)
            else:
                # Interpret empty result as closed connection
                print(f'closing {client_address} after reading no data')
                # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

                # Remove message queue
                del message_queues[s]
