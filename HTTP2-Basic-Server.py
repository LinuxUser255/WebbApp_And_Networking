#!/usr/bin/env python3

import json
import socket

import h2.connection
import h2.events
import h2.config

# This is a basic HTTP/2 Server that can accept inbound connections.
# This script is a from: https://python-hyper.org/projects/h2/en/stable/basic-usage.html#writing-your-server
# And formatted using black: https://pypi.org/project/black/
# However, it contains more explaination & Documentation in the form of Code Comments & Docstrings, than the original. 
# Annotations and type hints may be added later.
def send_response(conn, event):
    '''
    Take the H2Connection Object and the signaling event request
    H2 does not use unicode string, Except for Headers, which are auto encoded into UTF-8
    Send a response when a connection is received.
    This response will be set equal to data=
    '''
    # A stream_id is a bi-directional coms channel holding a request and response pair
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
    The H2Connection object writes data to an internal buffer
    and conn.initiate() sends a bit of data called the preamble.
    '''
    config = h2.config.H2Configuration(client_side=False)
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()
    sock.sendall(conn.data_to_send())

    while True:
        # recv has a max number/ammount of data it can take
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


# A socket object bound it to an address.
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', 8080))
sock.listen(5)

while True:
    handle(sock.accept()[0])
