BUFFER_SIZE = 1024

message_type_to_int_code = {
    "ok":1,
    "error": 2,
    "hi": 3,
    "kill": 4,
    "msg": 5,
    "creq": 6,
    "clist": 7,
    "origin": 8,
    "planet": 9,
    "planetlist": 10
}

int_code_to_message_type = {
    1: "ok",
    2: "error",
    3: "hi",
    4: "kill",
    5: "msg",
    6: "creq",
    7: "clist",
    8: "origin",
    9: "planet",
    10: "planetlist"
}

# Função que quebra o cabeçalho da mensagem e separa suas informações em um vetor
def decode_message(encoded_header):
    raw_data = encoded_header.decode('utf-8').split("|")
    data = list(map(int, raw_data[0:4]))
    if(len(raw_data) > 4):
        data.extend(raw_data[4:])
    return data


class Message_builder():
    def __init__(self):
        self.message = ""
        self.header = ""

    def add_header(self, new_header):
        if(len(self.header) != 0):
            self.header += f"|{new_header}"
        else:
            self.header = str(new_header) 
        return self

    def set_message(self, message):
        self.message = f"|{message}"
        return self

    def send(self, socket):
        data = self.header
        if(len(self.message) != 0):
            data += self.message
        socket.send(data.encode('utf-8'))
        self.message = self.header = ""

# Função comum ao emissor e receptor que envia a mensagem HI(3) para o servidor. 
# Retorna o ID que o servidor designou para o cliente ou dispara uma exceção, em caso de erro. 
def send_hi_message(socket, source_id, destination_id, sequence_num):
    Message_builder() \
        .add_header(message_type_to_int_code["hi"]) \
        .add_header(source_id) \
        .add_header(destination_id) \
        .add_header(sequence_num) \
        .send(socket)

    raw_response = socket.recv(BUFFER_SIZE)
    response = decode_message(raw_response)
    responde_code, _, designated_id, _, _ = response
    if(int_code_to_message_type[responde_code] == "ok"):
        return designated_id
    raise Exception("Erro ao enviar a mensagem \"hi\"")

def send_kill_message(socket, id, server_id, sequence_num):
    Message_builder() \
        .add_header(message_type_to_int_code["kill"]) \
        .add_header(id) \
        .add_header(server_id) \
        .add_header(sequence_num) \
        .send(socket)

    raw_response = socket.recv(BUFFER_SIZE)
    responde_code, _, _, _  = decode_message(raw_response)
    if(int_code_to_message_type[responde_code] != "ok"):
        raise Exception("Erro ao enviar a mensagem \"hi\"")

def send_origin_message(socket, id, server_id, sequence_num, planet_name_size, planet_name):
    Message_builder() \
        .add_header(message_type_to_int_code["origin"]) \
        .add_header(id) \
        .add_header(server_id) \
        .add_header(sequence_num) \
        .add_header(planet_name_size) \
        .set_message(planet_name) \
        .send(socket)

    raw_response = socket.recv(BUFFER_SIZE)
    responde_code, _, _, _ = decode_message(raw_response)
    if(int_code_to_message_type[responde_code] != "ok"):
        raise Exception("Erro ao enviar a mensagem \"origin\"")

def send_msg_message(socket, id, destination_id, sequence_num, msg_size, msg):
    Message_builder() \
        .add_header(message_type_to_int_code["msg"]) \
        .add_header(id) \
        .add_header(destination_id) \
        .add_header(sequence_num) \
        .add_header(msg_size) \
        .set_message(msg) \
        .send(socket)

def send_creq_message(socket, id, destination_id, sequence_num):
    Message_builder() \
        .add_header(message_type_to_int_code["creq"]) \
        .add_header(id) \
        .add_header(destination_id) \
        .add_header(sequence_num) \
        .send(socket)
    
    raw_response = socket.recv(BUFFER_SIZE)
    responde_code, _, _, _ = decode_message(raw_response)
    if(int_code_to_message_type[responde_code] != "ok"):
        raise Exception("Erro ao enviar a mensagem \"creq\"")

def send_clist_message(socket, id, destination_id, sequence_num, client_list):
    Message_builder() \
        .add_header(message_type_to_int_code["clist"]) \
        .add_header(id) \
        .add_header(destination_id) \
        .add_header(sequence_num) \
        .add_header(len(client_list)) \
        .set_message(client_list) \
        .send(socket)
    
    raw_response = socket.recv(BUFFER_SIZE)
    responde_code, _, _, _ = decode_message(raw_response)
    if(int_code_to_message_type[responde_code] != "ok"):
        raise Exception("Erro ao enviar a mensagem \"creq\"")

def send_planet_message(socket, id, client_id, sequence_num, planet=None):
    message = Message_builder() \
        .add_header(message_type_to_int_code["planet"]) \
        .add_header(id) \
        .add_header(client_id) \
        .add_header(sequence_num) \
    
    if(planet):
        message.set_message(planet)

    message.send(socket)

    if(not planet):
        raw_response = socket.recv(BUFFER_SIZE)
        responde_code, _, _, _ = decode_message(raw_response)
        if(int_code_to_message_type[responde_code] != "ok"):
            raise Exception("Erro ao enviar a mensagem \"planet\"")

def send_planetlist_message(socket, id, destination_id, sequence_num, planet_list=None, wait_for_ok_answer=False): 
    message = Message_builder() \
        .add_header(message_type_to_int_code["planetlist"]) \
        .add_header(id) \
        .add_header(destination_id) \
        .add_header(sequence_num) \

    if(planet_list):
        message.set_message(planet_list) 
    
    message.send(socket)


    if(wait_for_ok_answer):
        raw_response = socket.recv(BUFFER_SIZE)
        responde_code, _, _, _ = decode_message(raw_response)
        if(int_code_to_message_type[responde_code] != "ok"):
            raise Exception("Erro ao enviar a mensagem \"planet\"")

def send_ok_message(socket, source_id, destination_id, sequence_num, msg=None):
    message = Message_builder() \
        .add_header(message_type_to_int_code["ok"]) \
        .add_header(source_id) \
        .add_header(destination_id) \
        .add_header(sequence_num) \
        
    if(msg):
        message.set_message(msg)
    message.send(socket)

def send_error_message(socket, source_id, destination_id, sequence_num):
    Message_builder() \
        .add_header(message_type_to_int_code["error"]) \
        .add_header(source_id) \
        .add_header(destination_id) \
        .add_header(sequence_num) \
        .send(socket)