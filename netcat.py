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
