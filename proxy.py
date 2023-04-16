import socket
import urllib.parse as up
import utils as ut
import sys
import json 

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
    recv_message = ut.receive_full_message(new_socket,buff_size)

    m_recv = ut.http_to_map(recv_message)

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

            mod_message = ut.map_to_http(m_recv)

            newer_socket.send(mod_message.encode())

            response = ut.receive_full_message(newer_socket,buff_size)

            newer_socket.close()


            response = ut.http_to_map(response)
            if("Content-Length" in list(response.keys())):

                for item in data["forbidden_words"]:
                    key,value = list(item.items())[0]
                    response["Content"] = response["Content"].replace(key,value)
                
                response["Content-Length"] = str(len(response["Content"])+2)
            response = ut.map_to_http(response).encode()

            new_socket.send(response)
        

    new_socket.close()
