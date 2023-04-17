import socket
import urllib.parse as up
import sys
import json 

def http_to_map(http):
    result = {}
    end_of_firstline = http.find("\r\n")
    result["Start_Line"] = http[:end_of_firstline]
    start_line = http[:end_of_firstline]

    result["Method"] = start_line[:start_line.find(" ")]
    start_line = start_line[start_line.find(" ")+1:]
    result["Path"] = start_line[:start_line.find(" ")]
    start_line = start_line[start_line.find(" ")+1:]
    result["Version"] = start_line[:end_of_firstline]

    http = http[end_of_firstline+2:]

    while(True):
        index_end = http.find("\r\n")
        index_fin_heading = http.find(":")
        result[http[:index_fin_heading]]=http[index_fin_heading+2:index_end]
        http= http[index_end+2:]
        if (http[:2]=="\r\n"):
            http= http[2:]
            break
    if len(http)>0:
        result["Content"] = http
    return result



def map_to_http(map):
    result = ""
    result += map["Start_Line"] + "\r\n"
    del map["Start_Line"]
    del map["Method"]
    del map["Path"]
    del map["Version"]
    content = ""
    if "Content" in map:
        content += map["Content"]
        del map["Content"]
    for key, value in map.items():
        result += key+": "+ value +"\r\n"
    result+= "\r\n"
    result+= content
    return result

def receive_full_message(connection_socket, buff_size):

    fullmessage = connection_socket.recv(buff_size)
    mess_ended = fullmessage.decode().find("\r\n\r\n") >=  0

    while(not mess_ended):
        fullmessage += connection_socket.recv(buff_size)
        mess_ended =  fullmessage.decode().find("\r\n\r\n") >=  0

    hd_deco = fullmessage.decode()
    hd_end = hd_deco.find("\r\n\r\n") + 4
    header = hd_deco[:hd_end]
    map_http = http_to_map(header)

    if "Content-Length" in list(map_http.keys()):
        leftover = len(fullmessage) - hd_end
        cont_len = int(map_http["Content-Length"]) - leftover
        while(cont_len>0):
            fullmessage += connection_socket.recv(buff_size)
            cont_len -= buff_size
    return fullmessage.decode()

new_socket_address = ('localhost', 8000)
buff_size = 40

proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.bind(new_socket_address)
proxy_socket.listen(10)

path = ""
if len(sys.argv)==2:
    path = sys.argv[1]
    with open(path) as file:
        data = json.load(file)

while True: 
    new_socket, new_socket_address = proxy_socket.accept()
    recv_message = receive_full_message(new_socket,buff_size)

    m_recv = http_to_map(recv_message)

    if m_recv["Method"]=="GET":

        url = m_recv["Path"]

        if url in data["blocked"]:
            message = "HTTP/1.1 403 Forbidden\r\n\r\n"
            new_socket.send(message.encode())

        
        else:
            m_recv["X-ElQuePregunta"]="AtoTorga"

            host = up.urlparse(url).hostname

            newer_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

            newer_socket.connect((host,80))

            mod_message = map_to_http(m_recv)

            newer_socket.send(mod_message.encode())

            response = receive_full_message(newer_socket,buff_size)

            newer_socket.close()


            response = http_to_map(response)
            if("Content-Length" in list(response.keys())):

                for item in data["forbidden_words"]:
                    key,value = list(item.items())[0]
                    response["Content"] = response["Content"].replace(key,value)
                
                response["Content-Length"] = str(len(response["Content"])+2)
            response = map_to_http(response).encode()

            new_socket.send(response)
        

    new_socket.close()
