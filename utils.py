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
    

#Todo funcionando usar esto para debug.


# request = """GET / HTTP/1.1\r\nHost: www.example.com\r\nContent-Type: text/html; charset=UTF-8 \r\nUser-Agent: Mosaic/1.0\r\nCookie: PHPSESSID=298zf09hf012fh2; csrftoken=u32t403tb3gg43; _gat=1\r\n\r\n"""
# post =  """HTTP/1.1 200 OK\r\nDate: Mon, 23 May 2005 22:38:34 GMT\r\n Content-Type: text/html; charset=UTF-8\r\n Content-Length: 155\r\nLast-modified: Wed, 08 jan 2003 23:11:55 GMT\r\nServer: Apache/1.3.3.7 (Unix) (Red-Hat/Linux)\r\n ETag: "3f80f-1b6-3e1cb03b"\r\nAccept-Range: bytes\r\nConnection: close\r\n\r\n<html><head><title>An Example</title></head><body><p> Hello World, this is a very simple HTML document.</p></body></html>"""

# print("---------Request---------")
# req_map = http_to_map(request)
# print(req_map)
# print(map_to_http(req_map))
# print("-------------------------")
# print("-----------Post----------")
# post_map = http_to_map(post)
# print(post_map)
# print(map_to_http(post_map))
# print("-------------------------")