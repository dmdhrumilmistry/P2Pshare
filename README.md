# P2P Share

Peer to Peer file transfer over the network

## Installation
- Using pip and GitHub
  ```
  pip3 install git+https://github.com/dmdhrumilmistry/P2Pshare.git
  ```
- Clone Method
  - clone repo
    ```
    git clone --depth=1 https://github.com/dmdhrumilmistry/P2Pshare.git
    ```
  - change directory
    ```
    cd P2Pshare
    ```
  - install using pip
    ```
    pip3 install -e .
    ```

## Create Standalone
- Clone repo and change to repo directory
- Using pyinstaller
  ```bash
  pip3 install pyinstaller
  pyinstaller --onefile -n p2pshare/__main__.py
  ```
- Get executable from `dist` directory

## Usage

$ `python3 -m p2pshare`
```
usage: p2pshare [-h] [-i IP] [-p PORT] [-buff BUFF_SIZE] [-t {send,recv}] [-d SAVE_DIR] [-f FILE_PATH]
                   [-to TIMEOUT] [-conn CONNECTIONS]

Share files over the network between peers

options:
  -h, --help            show this help message and exit
  -i IP, --ip IP        ip address of the sender
  -p PORT, --port PORT  port of the sender
  -buff BUFF_SIZE, --buff-size BUFF_SIZE
                        Buffer Size
  -t {send,recv}, --type {send,recv}
                        Peer Type: send/recv
  -d SAVE_DIR, --directory SAVE_DIR
                        directory to save received files
  -f FILE_PATH, --file FILE_PATH
                        path of the file to be sent
  -to TIMEOUT, --timeout TIMEOUT
                        connection timeout
  -conn CONNECTIONS, --connections CONNECTIONS
                        number of simultaneous connections for sender
```
- examples
  - Send File
  `python3 -m p2pshare -t send -ip 192.168.10.27 -p 9898 -f myfile.ext`
  - Receive File
  `python3 -m p2pshare -t recv -ip 192.168.10.27 -p 9898 -d /home/user/Downloads`
  

## TODO
- Update README with instructions to transfer files over the internet using ngrok
