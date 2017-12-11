import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
execute = ""
target = ""
upload_destination = ""
port = 0


def usage():
    print ("Net Tool")
    print ()
    print ("Usage: netcat.py -t target_host - p port")
    print ("-l --listen -listen on[host]:[port] for incoming connections")
    print ("-e --execute = file_to_run -execute the given file upon receiving a connection")
    print ("-c --command    -initialize a command shell")
    print ("-u --upload = destination -upon receiving connection upload a file and write to [destination]")
    print ()
    print ()
    print ("Examples: ")
    print ("netcat.py -t 192.168.1.1 -p 1337 -l -u=c:\\target.exe")
    print ("netcat.py -t 192.168.1.1 -p 1337 -l -e=\"cat/etc/passwd\"")
    print ("echo 'ABCDEF'|./netcat.py -t 192.168.1.1. -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:", ["help", "listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print (str(err))
        usage()


    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e","--execute"):
            execute = a
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    buffer =sys.stdin.read()

    client_sender(buffer)
    if listen:
        server_loop()

main()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target,port))

        if len(buffer):
            client.send(buffer)

        while True:
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response+=data
                if recv_len < 4096:
                    break

            print(response)
            buffer = raw_input("")
            buffer +="\n"
            client.send(buffer)

    except:
        print("[*] Exception! Exiting")

        client.close()

def server_loop():
    global target
    if not len(target):
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    #trim the new line
    command = command.rstrip()

    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output = "Failed to execute command.\r\n"

    return (output)
