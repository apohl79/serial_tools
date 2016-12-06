#!/usr/bin/python -u
import sys, os, socket, stat, time

srv = 'localhost'
port = 99
script_dir = '/opt/433ctrl/scripts'

def read_code(file):
    print "Receiving code"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((srv, port))
    s.send('RCV\n')
    code = s.recv(1024)
    s.close()

    with open(file, "w") as f:
        f.write('/opt/serial_tools/send.py {} {} 1 "{}"\n'.format(srv, port, code.strip()))
        f.close()
        st = os.stat(file)
        os.chmod(file, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print "Done"

if len(sys.argv) != 2:
    print "Usage: {} name".format(sys.argv[0])
    exit(1)

name = sys.argv[1]
script_on = "{}/{}_on".format(script_dir, name)
script_off = "{}/{}_off".format(script_dir, name)

done = False

while not done:
    print "Press the ON key"
    read_code(script_on)
    time.sleep(1)
    print "Press the OFF key"
    read_code(script_off)
    time.sleep(1)
    print "Sending ON code"
    os.system(script_on)
    print "Did it work? (y/n) ",
    answer = sys.stdin.read(2).strip()
    if answer == 'n':
        print "\rOK we try it again"
        continue
    print "\rSending OFF code"
    os.system(script_off)
    print "Did it work? (y/n) ",
    answer = sys.stdin.read(2).strip()
    if answer == 'n':
        print "\rOK we try it again"
        continue
    print "\rGreat, we are done!"
    done = True
