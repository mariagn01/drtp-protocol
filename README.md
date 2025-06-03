# DATA2410 Reliable Transport Protocol (DRTP)

This project implements a reliable file transfer protocol (DRTP – DATA2410 Reliable Transport Protocol) in Python.
It supports reliable, in-order delivery of data between two nodes (a client and a server).

This is a part of the final exam in DATA2410 Networking and cloud computing (2025). 
Full details and requirements can be found here: https://github.com/safiqul/DRTP-v25


## Files
- application.py: Main program to start the client or server
- client.py: Client-side functions for connection, data transfer and teardown
- server.py: Server-side functions for connection, data transfer and teardown
- header.py: Functions related to creating a packet with a header, and parsing header and flags

## How to run
The client or server is run through the main program application.py. The file name, window size, server address and port number are given as command line arguments.

To run the server, use argument -s, with -i for IP-address and -p for port number. 

`python3 application.py -s -i <ip_address_of_the_server> -p <port>`

To run the client, use argument -c with -i for server IP-adress, -p for server port, -f for the file you wish to send, and -w for window size

`python3 application.py -c  -f <file> -i <ip_address_of_the_server> -p <server_port> -w <window_size>`

### Optional

To simulate packet loss and test retransmissions, you can instruct the server to discard a specific packet once using the -d flag:

`python3 application.py -s -i 10.0.1.2 -p 8080 -d 11`

This will cause the server to discard packet with sequence number 11 once.

### All arguments

| Short | Long        | Input       | Type    | Description                                                    |
| ----- | ----------- | ----------- | ------- |----------------------------------------------------------------|
| `-s`  | `--server`  |             | boolean | Run as server (receiver)                                       |
| `-c`  | `--client`  |             | boolean | Run as client (sender)                                         |
| `-i`  | `--ip`      | IP address  | string  | IP address to connect to (IPv4 or IPv6), default: 10.0.1.2             |
| `-p`  | `--port`    | Port number | int     | Port number. Must be in the range [1024, 65535], default: 8088 |
| `-f`  | `--file`    | File name   | string  | File to send (client only)                                     |
| `-w`  | `--window`  | Window size | int     | Sliding window size (default: 3)                               |
| `-d`  | `--discard` | Seq number  | int     | Server-only: discard a specific packet once (test case)        |
