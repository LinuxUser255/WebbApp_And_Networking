#!/usr/bin/env python3

import json
import socket
import h2.connection
import h2.events
import h2.config

# This is a basic HTTP/2 Server intended to serve as a high-level overview to the workings of the new version of the HTTP Protocol:
# HTTP/2, commonly referred to as H2.
# For the complete detailed technical overview of the HTTP/2 protocol see RFC 7540:
# https://datatracker.ietf.org/doc/html/rfc7540
# This script is a from: https://python-hyper.org/projects/h2/en/stable/basic-usage.html#writing-your-server
# And formatted using black: https://pypi.org/project/black/
# However, it contains more explaination & Documentation in the form of Code Comments & Docstrings, than the original script. 
# Usage: In one terminal run this script, and in another enter the following command: hyper --h2 GET http://localhost:8080/
def send_response(conn, event):
    '''
    Take the H2Connection Object and the signaling event request
    In order to store a request-response pair, a bi-directional coms channel called "stream_id is used.
    H2 does not use unicode string, Except for Headers, which are auto encoded into UTF-8
    Send a response when a connection is received.
    This response will be set equal to data=
    '''
    stream_id = event.stream_id
    response_data = json.dumps(dict(event.headers)).encode('utf-8')

    conn.send_headers(
        stream_id=stream_id,
        headers=[
            (':status', '200'),
            ('server', 'basic-h2-server/1.0'),
            ('content-length', str(len(response_data))),
            ('content-type', 'application/json'),
        ],
    )
    conn.send_data(
        stream_id=stream_id,
        data=response_data,   
        end_stream=True
    )

def handle(sock):
    '''
    This is an H2Connection object to receive & handle data. 
    That data is writen to an internal buffer
    The conn.initiate_connection() method establishes the connection and 
    sends a bit of data called the preamble.
    The recv function is used to read data from the socket 
    & has a max number/ammount of data it can take
    '''
    config = h2.config.H2Configuration(client_side=False)
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()
    sock.sendall(conn.data_to_send())

    while True:
        data = sock.recv(65535)
        if not data:
            break

        events = conn.receive_data(data)
        for event in events:
            if isinstance(event, h2.events.RequestReceived):
                send_response(conn, event)

        data_to_send = conn.data_to_send()
        if data_to_send:
            sock.sendall(data_to_send)


# A socket object bound to an address.
# This is the first block of code created when building this server.
# The goal is to sucessfully create something that can listen for a connection from a client.
# This is tested by running this script in one window, and curl http://localhost:8080/ and another.
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 8080))
sock.listen(5)

while True:
    handle(sock.accept()[0])
