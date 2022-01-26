import base64
import socket
import threading


class Sender:
    '''
    Class to send file over the network using TCP stream, over the network.
    '''
    def __init__(self, file_path:str, ip:str="0.0.0.0", port:int=9898, connections:int=5, buff_size:int=4096, timeout:float=5,) -> None:
        '''
        Description:
        ------------
            creates a Sender class object using passed args as configuration.

        Args:
        ------------
            ip (str): IPv4 address of the server
            port (int): port on which server will accept connections
            connections (int): to accept and handle number of simulataneous connections
            buff_size (int): size of the buffer for TCP connection
            timeout (float): timeout in seconds for particular TCP connection

        Returns:
        ------------
            None
        '''
        self.__file = file_path
        self.__ip = ip
        self.__port = port
        self.__connections = connections
        self.__buff_size = buff_size
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.settimeout(timeout)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def __handle_conn(self, conn:socket.socket, addr, print_conn_info:bool=True):
        '''
        Description:
        ------------
            handles a client and sends the requested file over the network using custom protocol.

        Args:
        ------------
            conn (socket.socket): A socket object of the accepted connection
            addr (_RetAddress): address of connected client
            print_conn_info (bool): decides whether to print connection details

        Returns:
        ------------
            None
        '''
        if print_conn_info:
            print(f"* Incoming from {addr[0]}:{addr[1]}")

        conn.send(b'ACK')
        data = conn.recv(self.__buff_size)
        print(data)
        if data == b'REC':
            # conn.send(b'Sending file')
            with open(self.__file, 'rb') as f:
                conn.send(self.__file.encode('utf-8'))
                file_data = f.read()
                file_data = base64.b64encode(file_data)
                file_size = str(len(file_data))
                print(file_size)
                conn.send(bytes(file_size, encoding='utf-8'))
                conn.sendall(file_data)
            data = conn.recv(self.__buff_size)
            print(data)
            if data == b'DACK':
                conn.send(b'Closing Conn')
                conn.close()
                return True
        return False

            
    def start(self):
        '''
        Description:
        ------------
            Binds and starts the server and handles incoming connection.

        Args:
        ------------
            None

        Returns:
        ------------
            None
        '''
        self.__server.bind((self.__ip, self.__port))
        self.__server.listen(self.__connections)
        while True:
            conn, addr =self.__server.accept()
            threading.Thread(target=self.__handle_conn, args=(conn, addr,) ).start()
            break


if __name__ == "__main__":
    import sys
    if sys.argv[1] == 'send':
        print(f"[*] Starting Sender on 0.0.0.0:9898 accepting 5 simulatenous connections with buffer size 4096 and 60seconds timeout")
        Sender(file_path='test.txt',timeout=None).start()
    elif sys.argv[1] == 'recv':
        print(f"Recvr")
    else:
        import textwrap
        print(textwrap.dedent('''
        Transfer module
        python3 -m P2Psharing.transfer [send|recv] [ip] [port]
        
        python3 -m P2Psharing.transfer sender 192.168.10.1 9898 myfile.txt
        python3 -m P2Psharing.transfer recv 192.168.10.1 9898'''))