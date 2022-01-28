from tqdm import tqdm

import argparse
import socket
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

        conn.send(b'ACK')

        # recv REC 
        data = conn.recv(self.__buff_size)
        if data == b'REC':
            with open(self.__file, 'rb') as f:
                file_size = os.path.getsize(self.__file)
                
                # send file name and date
                if os.name == 'nt':
                    file_name = self.__file.split('\\')[-1]
                else:
                    file_name = self.__file.split('/')[-1]
                conn.send(file_name.encode('utf-8'))
                # recv ACK
                data = conn.recv(self.__buff_size)
                
                
                conn.send(str(file_size).encode('utf-8'))
                # recv ACK
                data = conn.recv(self.__buff_size)
                time.sleep(0.00000000000000000000001)
                
                data_sent = 0
                progress = tqdm(range(file_size), desc=f"Sending {file_name}", unit='B', unit_scale=True, unit_divisor=1024)
                while data_sent < file_size:
                    file_data = f.read(self.__buff_size)
                    conn.sendall(file_data)
                    data_sent += self.__buff_size
                    progress.update(self.__buff_size)
                progress.desc = f'{file_name} Sent'
                progress.close()

            data = conn.recv(self.__buff_size)
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
        connected = 0
        while connected < self.__connections:
            conn, addr = self.__server.accept()
            threading.Thread(target=self.__handle_conn, args=(conn, addr,) ).start()
            connected += 1
        self.__server.close()


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
        # recv ack
        data = self.__client.recv(self.__buff_size)

        # send REC packet to confirm reception
        self.__client.send(b'REC')
        
        # accept file data
        file_name = self.__client.recv(self.__buff_size).decode('utf-8')
        self.__client.send(b'ACK')

        file_size = self.__client.recv(self.__buff_size)
        self.__client.send(b'ACK')
        file_size = int(file_size)

        file_data = b''
        progress = tqdm(range(file_size), desc=f"Receiving {file_name}", unit='B', unit_scale=True, unit_divisor=1024)
        while len(file_data) < file_size:
            data = self.__client.recv(self.__buff_size)
            file_data += data
            progress.update(self.__buff_size)
        progress.desc = f"{file_name} Received"
        progress.close()

        file_path = os.path.join(self.__save_dir, file_name)
        with open(file_path, 'wb') as f:
            f.write(file_data)

        self.__client.send(b'DACK')
        
        data = self.__client.recv(self.__buff_size)
        
        self.__client.close()

        return True


def start_command_line():
    '''
    Description:
    ------------
        Starts command line wrapper for p2pshare.transfer module

    Args:
    ------------
        None

    Returns:
    ------------
        None
    '''
    parser = argparse.ArgumentParser(
        prog='p2pshare',
        description='Share files over the network between peers',
    )

    parser.add_argument(
        '-i',
        '--ip',
        type=str,
        default='localhost',
        dest='ip',
        help='ip address of the sender'
    )

    parser.add_argument(
        '-p',
        '--port',
        type=int,
        default=9898,
        dest='port',
        help='port of the sender',
    )

    parser.add_argument(
        '-buff',
        '--buff-size',
        type=int,
        default=1048576,
        dest='buff_size',
        help='Buffer Size',
    )

    parser.add_argument(
        '-t',
        '--type',
        type=str,
        default='send',
        choices=['send', 'recv'],
        dest='type',
        help='Peer Type: send/recv',
    )

    parser.add_argument(
        '-d',
        '--directory',
        type=str,
        default=os.path.join(os.getcwd(),'saved_files'),
        dest='save_dir',
        help='directory to save received files',
    )

    parser.add_argument(
        '-f',
        '--file',
        type=str,
        default=None,
        dest='file_path',
        help='path of the file to be sent',
    )

    parser.add_argument(
        '-to',
        '--timeout',
        type=float,
        default=None,
        dest='timeout',
        help='connection timeout',
    )

    parser.add_argument(
        '-conn',
        '--connections',
        type=int,
        default=1,
        dest='connections',
        help='number of simultaneous connections for sender',
    )

    args = parser.parse_args()

    ip = args.ip
    port = args.port
    buff_size = args.buff_size
    peer_type = args.type
    save_dir = args.save_dir
    file_path = args.file_path
    connections = args.connections
    timeout = args.timeout

    if peer_type == 'send' and file_path is not None and os.path.exists(file_path):
        print(f"[*] Starting Sender on {ip}:{port} to send {file_path} file with {connections} connections.")
        Sender(file_path=file_path, ip=ip, port=port, connections=connections, buff_size=buff_size, timeout=timeout).start()
    elif peer_type == 'recv':
        print(f"[*] Connecting to {ip}:{port} with {buff_size} buffer size")
        Client(save_path=save_dir, ip=ip, port=port, buff_size=buff_size, timeout=timeout).receive()
    else:
        parser.print_help()
