from socket import *

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('localhost', 1234))
server_socket.listen(5)
server_socket.setblocking(0)

clients = []

while True:
   try:
       connection, address = server_socket.accept()
       connection.setblocking(0)

       client_name = connection.recv(1024).decode().strip()
       print(f"Підключився:{client_name}")
       if client_name:
           connection.send(f'Вітаю {client_name} в консольному чаті!'.encode())
           clients.append([connection, client_name])
   except:
       pass

   for client in clients[:]:
       try:
           message = client[0].recv(1024).decode().strip()
           for c in clients:
               if client != c:
                   c[0].send(f'{client[1]}: {message}'.encode())
       except BlockingIOError:
           pass
       except:
           print(f'Клієнт {client[1]} відключився.')
           client[0].close()
           clients.remove(client)



