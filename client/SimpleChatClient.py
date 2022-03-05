# Author: Elad Shoham
# I.D: 205439649

from socket import *

FORMAT = "utf-8"
WIND = 3
server = 'localhost'
serverPort = 5000

run = True

change = input(f"Server I.P: {server}, port: {serverPort} chang?\nyes: 1, no: 0\n")

if change == str(1):
    server = input("server I.P: ")
    serverPort = int(input("port: "))

name = input("Your name? ")
SERVER_ADDRESS = (server, serverPort)
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(SERVER_ADDRESS)

connectString = '<connect><' + name + '>'
clientSocket.send(connectString.encode(FORMAT))
firstMsg = clientSocket.recv(1024).decode(FORMAT)
print(firstMsg[1: -1])


def printInvalid():
    print("Invalid command")


def disconnect():
    clientSocket.send("<disconnect>".encode(FORMAT))
    answer = clientSocket.recv(1024).decode(FORMAT)
    print(answer)
    global run
    run = False


def getMsgLst():
    req = '<get_my_msgs>'
    clientSocket.send(req.encode(FORMAT))
    ans = clientSocket.recv(2048).decode(FORMAT)
    startSplitter = ans.find('>') + 1
    title = ans[: startSplitter]
    endSplitter = ans.find('>', startSplitter) + 1
    numOfMsgs = ans[startSplitter: endSplitter]
    print(title[1: -1] + '\n' + numOfMsgs[1: -1] + ' new massages:')
    startSplitter = endSplitter
    endSplitter = ans.find('>', startSplitter) + 1
    currentMsg = ans[startSplitter + 1: endSplitter - 1]
    while endSplitter < len(ans) and currentMsg != 'end':
        print(currentMsg)
        startSplitter = endSplitter
        endSplitter = ans.find('>', startSplitter) + 1
        currentMsg = ans[startSplitter + 1: endSplitter - 1]


def getUsersLst():
    req = '<get_users>'
    clientSocket.send(req.encode(FORMAT))
    ans = clientSocket.recv(2048).decode(FORMAT)
    startSplitter = ans.find('>') + 1
    title = ans[: startSplitter]
    endSplitter = ans.find('>', startSplitter) + 1
    numOfUsers = ans[startSplitter: endSplitter]
    print(title[1: -1] + '\n' + numOfUsers[1: -1] + ' users:')
    startSplitter = endSplitter
    endSplitter = ans.find('>', startSplitter) + 1
    userName = ans[startSplitter + 1: endSplitter - 1]
    while endSplitter < len(ans) and userName != 'end':
        print(ans[startSplitter + 1: endSplitter - 1])
        startSplitter = endSplitter
        endSplitter = ans.find('>', startSplitter) + 1
        userName = ans[startSplitter + 1: endSplitter - 1]


def sendMsg():
    toWho = input("send massage to(if  to all insert 'all'): ")
    massage = input('Massage: \n')
    if toWho == 'all':
        req = '<set_msg_all >'
    else:
        req = '<set_msg><' + toWho + '>'
    req = req + '<' + massage + '>'
    clientSocket.send(req.encode(FORMAT))
    ans = clientSocket.recv(2048).decode(FORMAT)
    print(ans[1: -1])


def getFilesList():
    req = '<get_list_file>'
    clientSocket.send(req.encode(FORMAT))
    ans = clientSocket.recv(2048).decode(FORMAT)
    startSplitter = ans.find('>') + 1
    title = ans[1: startSplitter - 1]
    print(title)
    print('\n')
    endSplitter = ans.find('>', startSplitter) + 1
    fileName = ans[startSplitter + 1: endSplitter - 1]
    while fileName != 'end' and endSplitter < len(ans):
        print(fileName)
        startSplitter = endSplitter
        endSplitter = ans.find('>', startSplitter + 1) + 1
        fileName = ans[startSplitter + 1: endSplitter - 1]


def downloadFile(fileName, portNum):
    msg = clientSocket.recv(1024).decode(FORMAT)
    if msg == '<didnt_find_file>':
        return
    address = (server, portNum)
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.sendto('<connected>'.encode(FORMAT), address)
    message, serverAddress = sock.recvfrom(2048)
    try:
        f = open(fileName, 'x')
    except:
        sock.sendto('<file_already_exist>'.encode(FORMAT), address)
        sock.close()
        return
    f.close()
    sock.sendto('<send>'.encode(FORMAT), address)
    file = open(fileName, 'ab')
    try:
        message, serverAddress = sock.recvfrom(1024)
    except:
        sock.sendto('<NACK>'.encode(FORMAT), address)
    while message != b'':
        sock.sendto('<ACK>'.encode(FORMAT), address)
        file.write(message)
        message, serverAddress = sock.recvfrom(1024)
    file.close()
    sock.close()


def getFile():
    fileName = input("Which file would you like to download?\n")
    clientSocket.send(f'<download><{fileName}>'.encode(FORMAT))
    ans = clientSocket.recv(1024).decode(FORMAT)
    startSplitter = ans.find('>') + 1
    endSplitter = ans.find('>', startSplitter)
    myPort = ans[startSplitter + 1: endSplitter]
    downloadFile(fileName, int(myPort))
    status = clientSocket.recv(1024).decode(FORMAT)
    if status == '<File_sent_successfully>':
        print('File downloaded')
    else:
        print(status[1: -1])


switcher = {
    1: disconnect,
    2: getMsgLst,
    3: getUsersLst,
    4: sendMsg,
    5: getFilesList,
    6: getFile
}


def startChat():
    while run:
        print("Choose an option:")
        for command in switcher:
            print(f"{command}: {switcher[command].__name__}")
        chosen = input()
        switcher.get(int(chosen), printInvalid)()
    print(clientSocket.recv(2048).decode(FORMAT))
    clientSocket.close()


startChat()
