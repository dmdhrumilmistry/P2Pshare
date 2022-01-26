import base64
import socket
import sys
import threading
import time
import os


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

        # server socket configuration
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

        print('* Sending ACK')
        conn.send(b'ACK')

        print('* Receiving REC packet')
        data = conn.recv(self.__buff_size)
        print(data)
        if data == b'REC':
            # conn.send(b'Sending file')

            with open(self.__file, 'rb') as f:
                # file_data = f.read()
                # file_data = base64.b64encode(file_data)
                # file_size = str(len(file_data))
                file_size = os.path.getsize(self.__file)
                print(file_size)
                
                # send file name and date
                print('* Sending File name')
                conn.send(self.__file.encode('utf-8'))
                print('* Sending File size')
                conn.send(str(file_size).encode('utf-8'))
                time.sleep(0.00000000000000000000001)
                
                print('* Sending File')
                data_sent = 0
                while data_sent < file_size:
                    file_data = f.read(self.__buff_size)
                    file_data = base64.b64encode(file_data)
                    conn.sendall(file_data)
                    data_sent += self.__buff_size
                    # TODO: Update progress bar

            print('* Waiting for DACK')
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

class Client:
    '''
    Class to receive sent files over the network
    '''
    def __init__(self, save_path:str, ip:str="localhost", port:int=9898, buff_size:int=4096, timeout:float=5,) -> None:
        '''
        Description:
        ------------
            creates a Receiver class object using passed args as configuration.

        Args:
        ------------
            save_path (str): path of directory to save received files
            ip (str): IPv4 address of the server
            port (int): port on which server will accept connections
            buff_size (int): size of the buffer for TCP connection
            timeout (float): timeout in seconds for particular TCP connection

        Returns:
        ------------
            None
        '''
        self.__save_dir = save_path
        self.__ip = ip
        self.__port = port
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__buff_size = buff_size

        # client socket configuration
        self.__client.settimeout(timeout)
        self.__client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # create save dir if dir does not exist
        if not os.path.exists(self.__save_dir):
            os.mkdir(self.__save_dir)

    def receive(self,) -> bool:
        '''
        Description:
        ------------
            Start receiving file sent by the sender

        Args:
        ------------
            None

        Returns:
        ------------
            bool
        '''
        self.__client.connect((self.__ip, self.__port))
        data = self.__client.recv(self.__buff_size)
        print(data)

        # send REC packet to confirm reception
        print('* Sending REC packet')
        self.__client.send(b'REC')
        
        # accept file data
        print('* Receiving File name')
        file_name = self.__client.recv(self.__buff_size).decode('utf-8')
        print(file_name)

        print('* Receiving File size')
        file_size = self.__client.recv(self.__buff_size)
        print(file_size)
        file_size = int(file_size)

        print('* Receiving File contents')
        file_data = b''
        while len(file_data) < file_size:
            data = self.__client.recv(self.__buff_size)
            if len(data) <= 0:
                break
            file_data += data
            print(data)
        
        file_data = base64.b64decode(file_data)
        print(file_data)

        print('* Sending DACK packet')
        self.__client.send(b'DACK')
        
        print('* Receiving closing packet')
        data = self.__client.recv(self.__buff_size)
        
        print('* Closing Client socket')
        self.__client.close()

        return True


if __name__ == "__main__":
    if sys.argv[1] == 'send':
        print(f"[*] Starting Sender on 0.0.0.0:9898 accepting 5 simulatenous connections with buffer size 4096 and 60seconds timeout")
        Sender(file_path='test.txt',timeout=None).start()
    elif sys.argv[1] == 'recv':
        Client(save_path='test_dir').receive()
    else:
        import textwrap
        print(textwrap.dedent('''
        Transfer module
        python3 -m P2Psharing.transfer [send|recv] [ip] [port]
        
        python3 -m P2Psharing.transfer sender 192.168.10.1 9898 myfile.txt
        python3 -m P2Psharing.transfer recv 192.168.10.1 9898'''))