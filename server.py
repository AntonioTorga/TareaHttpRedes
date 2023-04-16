import socket
import utils as ut
import sys
import json 

new_socket_address = ('localhost', 8000)
buff_size = 2048

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(new_socket_address)
server_socket.listen(2)

path = ""
if len(sys.argv)==2:
    path = sys.argv[1]
    print(path)
    with open(path) as file:
        data = json.load(file)


while True: 
    new_socket, new_socket_address = server_socket.accept()
    recv_message = new_socket.recv(buff_size)
    
    map = ut.html_to_map(recv_message.decode())

    if map["Method"] == "GET":
        message = """HTTP/1.1 200 OK\r\nDate: Mon, 23 May 2005 22:38:34 GMT Content-Type: text/html; charset=UTF-8 Content-Length: 155\r\nLast-modified: Wed, 08 jan 2003 23:11:55 GMT Server: Apache/1.3.3.7 (Unix) (Red-Hat/Linux) ETag: "3f80f-1b6-3e1cb03b"\r\nAccept-Range: bytes Connection: close\r\n\r\n<html><head><title>An Example</title></head><body><p> Hello World, this is a very simple HTML document.</p></body></html>"""
        message2 = """HTTP/1.1 200 OK\r\nAge: 52135\r\nCache-Control: max-age=604800\r\nContent-Type: text/html; charset=UTF-8\r\nDate: Sat, 08 Apr 2023 00:35:59 GMT\r\nEtag: "3147526947+gzip+ident"\r\nExpires: Sat, 15 Apr 2023 00:35:59 GMT\r\nLast-Modified: Thu, 17 Oct 2019 07:18:26 GMT\r\nServer: ECS (mic/9ABC)\r\nVary: Accept-Encoding\r\nX-Cache: HIT\r\nContent-Length: 1256\r\n\r\n
<!doctype html><html><head><title>Example Domain</title><meta charset="utf-8" /><meta http-equiv="Content-type" content="text/html; charset=utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><style type="text/css">
body {
background-color: #f0f0f2;
margin: 0;
padding: 0;
font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;

}
div {
width: 600px;
margin: 5em auto;
padding: 2em;
background-color: #fdfdff;
border-radius: 0.5em;
box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);
}
a:link, a:visited {
color: #38488f;
text-decoration: none;
}
@media (max-width: 700px) {
div {
    margin: 0 auto;
    width: auto;
}
}
</style>    
</head>

<body>
<div>
<h1>Example Domain</h1>
<p>This domain is for use in illustrative examples in documents. You may use this
domain in literature without prior coordination or asking for permission.</p>
<p><a href="https://www.iana.org/domains/example">More information...</a></p>
</div>
</body>
</html>
"""
        map2 = ut.html_to_map(message2)
        map2["X-ElQuePregunta"] = data["Name"] if data else "Antonio Torga"        
        message2 = ut.map_to_html(map2)
        new_socket.send(message2.encode())

    new_socket.close()
