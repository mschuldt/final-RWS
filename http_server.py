import SimpleHTTPServer
import SocketServer
import logging
import util
import thread
import uuid
import os
import time
import requests
import json
from interpreter import run_program

USE_MSGPACK = False

def clientthread(json_dict, addr):
    data = json_dict

    process_count = 0
    md = {}
    md['/processes3'] = {'uuid': str(uuid.uuid1()),
                        'Metadata': {'SourceName': 'interpreter3'},
                        'Properties': {'UnitofTime': 'ms', 'UnitofMeasure': 'count'}}

    # We don't want to generate new uuids on every run, just the first
    if os.path.exists('.smap_interpreter'):
        addresses = json.load(open('.smap_interpreter'))
    else:
        addresses = md
        json.dump(addresses, open('.smap_interpreter','wb'))

    while True:
        #data, addr = sock.recvfrom(buffer_size)
        if USE_MSGPACK:
            msg = msgpack.unpackb(data)
        else:
            msg = data
        #print "RECEIVED>>>", msg
        #print "FROM>>>", addr

        if str(msg.get('password')) != "password":
            print("Authentication failed")
            continue

        if not all([msg.get(x) for x in ['initial', 'connections', 'nodes']]):
            print("Invalid program, ignoring.")
            #print("msg = ",msg)
            continue

        smap = {}
        processes = smap['/processes3'] = addresses['/processes3']
        process_count += 1
        processes['Readings'] = [[int(time.time()*1000), process_count]]

        try:
            # We use the IPv4 address because requests sometimes defaults
            # to ipv6 if you use DNS and the archiver doesn't support that.
            # This is a hack

            print "sending this to archiver: ", json.dumps(smap)

            x = requests.post('http://54.215.11.207:8079/add/interpreter',
            #x = requests.post('http://shell.storm.pm:8079/add/interpreter',
                              data=json.dumps(smap))
            #x = requests.post('http://pantry.cs.berkeley.edu:8079/add/xyz',
            #                  data=json.dumps(smap))
            print "archiver: ", x
        except Exception as e:
            print (e)

        run_program(msg)    


PORT = 1444
class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_POST(self):
        logging.warning("======= POST STARTED =======")
        logging.warning(self.headers)

        # load post content 
        length = int(self.headers['Content-length'])
        post_content = self.rfile.read(length)

        # object is a dictionary 
        json_dict = util.load_json(post_content)
        
        # iterate through available values 
        #for i in json_dict.keys():
        #    print(str(i) + " " + str(json_dict[i]))

        # feed client address into threadable function
        client_addr = str(self.client_address[0]) + ":" + str(self.client_address[1])

        thread.start_new_thread(clientthread ,(json_dict,client_addr))

        self.send_response(200)
        

Handler = ServerHandler

httpd = SocketServer.TCPServer(("127.0.0.1", PORT), Handler)

print("Server active")
httpd.serve_forever()


# 




'''
if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 1444
    I = ""


PORT = 1444
class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.warning("======= GET STARTED =======")
        logging.warning(self.headers)
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        logging.warning("======= POST STARTED =======")
        logging.warning(self.headers)
        length = int(self.headers['Content-length'])
        post_content = self.rfile.read(length)

        obj = util.load_json(post_content)
        print(type(obj))

        for i in obj.keys():
            print(str(i) + " " + str(obj[i]))
        

        print(type(obj))
        print(self.rfile.read(length))
        print(self.headers.keys())
        print(dir(self.headers))
        print(self.headers)
        print(type(self))
        print(dir(self))

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        logging.warning("======= POST VALUES =======")
        print(form)
        for item in form.list:
            logging.warning(item)
        logging.warning("\n")
        
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "@rochacbruno Python http server version 0.1 (for testing purposes only)"
print "Serving at: http://%(interface)s:%(port)s" % dict(interface=I or "localhost", port=PORT)
httpd.serve_forever()

'''