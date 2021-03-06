PORT='1459'

import json
import urllib2
import time

program1 = {'type':'program',
           'uid': 'rws',
           'password': 'password',
           'pid':'1',
           #a list of the nodes that are ready to run.
           #These are the nodes that don't have a parent.
           'initial': ['n0', 'n1'],
           #'connections' maps wires to lists of nodes that are connected to them
           'connections':{'w0' : ['n2'],
                          'w1' : ['n2'],
                          'w2' : ['n3']},
           #mapping of node IDs to nodes
           # each node must have a 'type' field.
           # some other node fields:
           #    'out': the id of the nodes output wire, if any
           #           we currently only support 1 output
           #     'in': a list of the nodes input wires, if any
           'nodes':{'n0' : {'type': 'literal',
                            'val': 4,
                            'outputs': ['w0']},
                    'n1' : {'type': 'literal',
                            'val': 8,
                            'outputs': ['w1']},
                    'n2' : {'type': 'binop',
                            'op': '+',
                            'inputs':['w0', 'w1'],
                            'outputs': ['w2']},
                    'n3' : {'type': 'call',
                            'name': 'print',
                            'inputs': ['w2']}}}

program1_start = {'uid': 'rws',
                  'pid': '1',
                  'password': 'password'}


#this program subscribes to a sine wave smap source,
#multiplies it by 100 and prints that values
program2 = {'type':'program',
            'uid': 'rws',
            'password': 'password',
            'pid':'2',
            'initial': ['n0', 'n1'],
            'connections':{'w0' : ['n2'],
                           'w1' : ['n2'],
                           'w2' : ['n3']},
            'nodes':{'n0' : {'type': 'smap',
                             'smap-type': 'subscribe',
                             'url': 'ws://shell.storm.pm:8078/republish',
                             'uuid': '71be455c-2eac-50d3-ac03-81fae87b0ee3',
                             'outputs': ['w0']},
                     'n1' : {'type': 'literal',
                             'val': 100,
                             'outputs': ['w1']},
                     'n2' : {'type': 'binop',
                             'op': '*',
                             'inputs':['w0', 'w1'],
                             'outputs': ['w2']},
                     'n3' : {'type': 'call',
                             'name': 'print',
                             'inputs': ['w2']}}}

program2_start = {'uid': 'rws',
                  'pid': '2',
                  'password': 'password'}


#this program reads from the sine wave source, multiples that by 100
# and turns turns a light on if it is even, otherwise turns it off
program3 = {'type':'program',
            'uid': 'rws',
            'password': 'password',
            'pid':'3',
            'initial': ['n0', 'n1'],
            'connections':{'w0' : ['n2'],
                           'w1' : ['n2'],
                           'w2' : ['n3', 'n4'],
                           'w3' : ['n4'],
                           'w4' : ['n5']},
            'nodes':{'n0' : {'type': 'smap',
                             'smap-type': 'subscribe',
                             'url': 'ws://shell.storm.pm:8078/republish',
                             ##our sine wave driver:
                             'uuid': '8227497f-34bf-54a9-94e4-b1d1a9fe9fd2',
                             ##Gabes sine wave driver:
                             #'uuid': '71be455c-2eac-50d3-ac03-81fae87b0ee3'
                             'outputs': ['w0']},
                     'n1' : {'type': 'literal',
                             'val': 100,
                             'outputs': ['w1']},
                     'n2' : {'type': 'binop',
                             'op': '*',
                             'inputs':['w0', 'w1'],
                             'outputs': ['w2']},
                     'n3' : {'type': 'call',
                             'name': 'even?',
                             'inputs': ['w2'],
                             'outputs':['w4']},

                     'n4' : {'type': 'smap',
                             'smap-type': 'actuate',
                             ##uuid for inventation lab plugstrip7(desk lamp)
                             #'uuid': '52edbef3-98e9-5cef-8cc9-9ddee810cd5d',

                             # our test driver
                             'uuid': 'ee52a387-905a-5a63-9b86-afb53414e702',

                             'inputs': ['w4']},
                     #print even?
                     'n5' : {'type': 'call',
                             'name': 'print',
                             'inputs': ['w4']}
                 }}

program3_start = {'uid': 'rws',
                  'pid': '3',
                  'password': 'password'}

#led strip demo program
#reads from our sine save source which has amplitude of 0.5,
#adds 0.5, multiples by 10, modulo 32, then sends that
#value to the led strip actuator stream.
#equivalent to:
# led_strip_set(((sine_wave() + 0.5)*10) %32)
program4 = {'type':'program',
            'uid': 'rws',
            'password': 'password',
            'pid':'4',
            'initial': ['n0', 'n1', 'n3', 'n8'],
            'connections':{'w0' : ['n2'],
                           'w1' : ['n2'],
                           'w2' : ['n6'],
                           'w3' : ['n6'],
                           'w8' : ['n4', 'n5'],
                           'w4' : ['n7'],
                           'w5' : ['n7']},
            'nodes':{'n0' : {'type': 'smap',
                             'smap-type': 'subscribe',
                             'url': 'ws://shell.storm.pm:8078/republish',
                             ##our sine wave driver:
                             #'uuid': '8227497f-34bf-54a9-94e4-b1d1a9fe9fd2',
                             'uuid': '024fdb52-617f-5714-b5a1-c80774e60ea5',
                             'outputs': ['w0']},
                     'n1' : {'type': 'literal',
                             'val': 0.5,
                             'outputs': ['w1']},
                     'n2' : {'type': 'binop',
                             'op': '+',
                             'inputs':['w0', 'w1'],
                             'outputs': ['w2']},

                     'n3' : {'type': 'literal',
                             'val': 10,#100,
                             'outputs': ['w3']},
                     'n6' : {'type': 'binop',
                             'op': '*',
                             'inputs':['w3', 'w2'],
                             'outputs': ['w5']},

                     'n8' : {'type': 'literal',
                             'val': 32,
                             'outputs': ['w4']},
                     'n7' : {'type': 'binop',
                             'op': '%',
                             'inputs':['w5', 'w4'],
                             'outputs': ['w8']},

                     'n4' : {'type': 'smap',
                             'smap-type': 'actuate',
                             # 'streetlight' driver
                             #Andrews version:
                             'uuid': 'ac903027-3a81-5d2f-a5cb-7983f5fb9f0a',
                             #'uuid': '4caee96b-31fc-540b-9210-5160d19f2af2',
                             'inputs': ['w8']},

                     'n5' : {'type': 'call',
                             'name': 'print',
                             'inputs': ['w8']}
                 }}

program4_start = {'uid': 'rws',
                  'pid': '4',
                  'password': 'password'}

################################################################################
#program = program1
#program = program2
#program = program3
program = program4

#start = program1_start
#start = program2_start
#start = program3_start
start = program4_start


req = urllib2.Request('http://10.142.34.191:'+PORT)
req = urllib2.Request('http://127.0.0.1:'+PORT)
send_req = urllib2.Request('http://127.0.0.1:'+PORT+'/new')
start_req = urllib2.Request('http://127.0.0.1:'+PORT+'/start')
status_req = urllib2.Request('http://127.0.0.1:'+PORT+'/status')
list_req = urllib2.Request('http://127.0.0.1:'+PORT+'/list_programs')

req.add_header('Content-Type', 'application/json')

print "sending program..."
print urllib2.urlopen(send_req, json.dumps(program)).read()

print "starting program..."
print urllib2.urlopen(start_req, json.dumps(start)).read()

print "querying status..."
print urllib2.urlopen(status_req, json.dumps(start)).read()

time.sleep(1)

print "querying status..."
print urllib2.urlopen(status_req, json.dumps(start)).read()


print "listing programs..."
print urllib2.urlopen(list_req, json.dumps({'uid': 'rws', 'password': 'password' })).read()
