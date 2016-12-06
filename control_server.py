#!/usr/bin/python -u
import sys, socket, serial, threading
from optparse import OptionParser

ser1 = None
ser2 = None

def ctrl_master(ser, master):
    while True:
        (clnt, addr) = master.accept()
        threading.Thread(target = lambda: ctrl_handler(ser, clnt)).start()

def ctrl_handler(ser, clnt):
    data = clnt.recv(1024)
    print "Sending command to serial controller"
    try:
        #print "<- {}".format(data),
        ser.write(data)
        ret = ser.readline()
        #print "-> {}".format(ret),
        clnt.send(ret)
    except Exception as e:
        print "error: {}".format(e.strerror)
    clnt.close()

parser = OptionParser(usage="Usage: %prog [options]")
parser.add_option("-d", "--devices", dest="devs",
                  help="Number of devices to connect to. Possible values are 1 and 2. (Default: 1)",
                  default=1)
(opts, args) = parser.parse_args()

print "Opening serial port(s):"
ser1 = serial.Serial("/dev/ttyUSB0", timeout=3)
if int(opts.devs) > 1:
    ser2 = serial.Serial("/dev/ttyUSB1", timeout=3)

# Find the 433 controller to make sure it is ser2
ser1.write(b'INFO\r\n')
ret = ser1.readline()
if ret == "433RT":
    if int(opts.devs) > 1:
        serx = ser1
        ser2 = ser1
        ser1 = serx
        print "IR controller on ttyUSB1"
    print "433 controller on ttyUSB0"
else:
    print "IR controller on ttyUSB0"
    if int(opts.devs) > 1:
        print "433 controller on ttyUSB1"

print "Staring control server"
# Control server to be connected by the send script/openhab
master1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
master1.bind(("", 99))
master1.listen(8)
threading.Thread(target = lambda: ctrl_master(ser1, master1)).start()

if int(opts.devs) > 1:
    master2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master2.bind(("", 100))
    master2.listen(8)
    threading.Thread(target = lambda: ctrl_master(ser2, master2)).start()

