# Author: Elad Shoham
# I.D: 205439649

from socket import *
import threading

FORMAT = "utf-8"
port = 5000
BUFFER_SIZE = (64 * 1024 - 1 - 20 - 8) * 8

# a list to hold all the clients and their names
clients = {}

# list to hold all the new messages
msgs = {}
files = {'64kb.txt', 'img1.png'}
ports = {
    55000: 0,
    55001: 0,
    55002: 0,
    55003: 0,
    55004: 0,
    55005: 0,
    55006: 0,
    55007: 0,
    55008: 0,
    55009: 0,
    55010: 0,
    55011: 0,
    55012: 0,
    55013: 0,
    55014: 0,
    55015: 0
}


def sendFiles(myPort, path, client):
    try:
        file = open('server/' + path, "rb")
    except:
        clients[client].send('<didnt_find_file>'.encode(FORMAT))
        return f'<ERROR: could not open file "{path}">'
    SERVER_ADDRESS = ('', myPort)
    mySocket = socket(AF_INET, SOCK_DGRAM)
    mySocket.bind(SERVER_ADDRESS)
    clients[client].send('<UDP_opened>'.encode(FORMAT))
    message, clientAddress = mySocket.recvfrom(2048)
    mySocket.sendto('<ready_to_send>'.encode(FORMAT), clientAddress)
    message, clientAddress = mySocket.recvfrom(2048)
    if message == '<file_already_exist>'.encode(FORMAT):
        mySocket.close()
        file.close()
        return '<file_already_exist>'
    pack = file.read(1024)
    while pack != b"":
        mySocket.sendto(pack, clientAddress)
        try:
            mySocket.settimeout(0.5)
            message, clientAddress = mySocket.recvfrom(1024)
        except:
            message = '<send_again>'.encode(FORMAT)
        mySocket.settimeout(0)
        if message == '<ACK>'.encode(FORMAT):
            pack = file.read(1024)
    mySocket.sendto(pack, clientAddress)
    file.close()
    mySocket.close()
    return '<File_sent_successfully>'


# restOfMsg = <to who?><message>
def broadcastTo(restOfMsg, client):
    splitter = restOfMsg.find('>') + 1
    sendTo = restOfMsg[1: splitter - 1]
    msg = '<' + client + ': ' + restOfMsg[splitter + 1:] + '>'
    global msgs
    msgs[sendTo]['m'] = msgs[sendTo]['m'] + msg
    msgs[sendTo]['count'] = msgs[sendTo]['count'] + 1
    clients[client].send('<massage_sent>'.encode(FORMAT))


# restOfMsg = <message>
def broadcastToAll(restOfMsg, client):
    global msgs
    for c in msgs.values():
        msg = restOfMsg[0] + client + ': ' + restOfMsg[1:]
        c['m'] = c['m'] + msg
        c['count'] = c['count'] + 1
    clients[client].send('<massage_sent_to_all>'.encode(FORMAT))


def broadcastToAllAno(msg, fromWho):
    global msgs
    msg = msg[0] + fromWho + ': ' + msg[1:]
    for c in msgs.values():
        c['m'] = c['m'] + msg
        c['count'] = c['count'] + 1


# send: <users_lst><num of users><list>
def getAllUsers(restOfMsg, client):
    message = '<users_lst><' + str(len(clients)) + '>'
    for n in clients.keys():
        message = message + f'<{n}>'
    message = message + '<end>'
    clients[client].send(message.encode(FORMAT))


def invalidCommand(restOfMsg, client):
    print(f"{client} sent an Invalid request")
    message = '<Invalid request>'
    clients[client].send(message.encode(FORMAT))


# send: <msg_lst><num of msgs><all the msgs>
def getMessages(restOfMsg, client):
    allMsg = '<msg_lst><' + str(msgs[client]['count']) + '>' + msgs[client]['m'] + '<end>'
    clients[client].send(allMsg.encode(FORMAT))
    msgs[client]['m'] = ''
    msgs[client]['count'] = 0


def sendFilesList(restOfMsg, client):
    ans = '<file_lst>'
    for file in files:
        ans = ans + '<' + file + '>'
    ans = ans + '<end>'
    clients[client].send(ans.encode(FORMAT))


def findFreePort():
    finder = 55000
    flag = ports[finder]
    while flag == 1:
        finder = finder + 1
        if finder > 55015:
            finder = 55000
        flag = ports[finder]
    ports[finder] = 1
    return finder


def downloadFile(restOfMsg, client):
    filePath = restOfMsg[1: -1]
    freePort = findFreePort()
    clients[client].send(f'<port><{freePort}>'.encode(FORMAT))
    ans = sendFiles(freePort, filePath, client)
    ports[freePort] = 0
    clients[client].send(ans.encode(FORMAT))


switcher = {
    '<set_msg_all >': broadcastToAll,
    '<get_users>': getAllUsers,
    '<set_msg>': broadcastTo,
    '<get_my_msgs>': getMessages,
    '<get_list_file>': sendFilesList,
    '<download>': downloadFile
}


def handleClient(client, addr):
    run = True
    while run:
        request = clients[client].recv(1024).decode(FORMAT)
        splitter = request.find('>') + 1
        command = request[: splitter]
        rest = request[splitter:]
        if command == '<disconnect>':
            run = False
        else:
            switcher.get(command, invalidCommand)(rest, client)
    broadcastToAllAno('<disconnected>', client)
    clients[client].send('<disconnected>'.encode(FORMAT))
    clients[client].close()
    clients.pop(client)
    msgs.pop(client)


serverAddress = ('', port)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

serverSocket.listen(1)
print(f"The server is ready to receive clients at port: {port}")

while True:
    connectionSocket, addrClient = serverSocket.accept()
    receivedMsg = connectionSocket.recv(1024).decode(FORMAT)
    # we know the first message will be: <connect><the name>
    name = receivedMsg[10: -1]
    connectionSocket.send("<connected>".encode(FORMAT))
    clients[name] = connectionSocket
    msgs[name] = {'m': '', 'count': 0}
    broadcastToAllAno('<connected>', name)
    thread = threading.Thread(target=handleClient, args=(name, addrClient))
    thread.start()
