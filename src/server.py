from socket import *
from header import * # Import functions for header creation and parsing
import time

"""Description: Function that returns the current time in HH:MM:SS.MMMMMM format"""
def current_time():
    return time.strftime("%H:%M:%S.", time.localtime()) + str(int(time.time() * 1000000) % 1000000)

"""Description: A three-way handshake with the client to establish a connection
Arguments: the UDP socket, and a window size to use if not negotiated, default set to 15.
Returns True if the handshake completes successfully, false otherwise."""
def three_way_handshake(sock, default_window=15):
    try:
        sock.settimeout(30)  # Total handshake timeout
        #Wait for SYN
        while True:
            try:
                packet, addr = sock.recvfrom(8)
            except timeout:
                print("Handshake failed: No SYN received")
                return False

            seq, ack, flags, win = parse_header(packet)
            syn_flag, ack_flag, fin_flag = parse_flags(flags)

            if syn_flag and not ack_flag:
                print("SYN packet is received")

                #Send SYN-ACK
                negotiated_win = min(win, default_window) # Sets window size to the smaller of received and default
                syn_ack = create_packet(0, 0, SYN | ACK, negotiated_win, b'')
                sock.sendto(syn_ack, addr)
                print("SYN-ACK packet is sent")

                #Wait for ACK
                sock.settimeout(3)  # Timeout after 3s if no ACK is received
                try:
                    packet, addr = sock.recvfrom(8)
                    seq, ack, flags, win = parse_header(packet)
                    syn_flag, ack_flag, fin_flag = parse_flags(flags)

                    if ack_flag and not syn_flag:
                        print("ACK packet is received")
                        print("Connection established")
                        return True
                    else:
                        print("ACK was not received correctly")
                except timeout:
                    print("Timeout waiting for ACK, client unresponsive")
            else:
                print("Unexpected packet during handshake")
    except Exception as e:  # Any other unexpected error
        print(f"Handshake error: {e}")
        return False

"""Description: Function for closing the connection after receiving FIN.
Arguments: The UDP socket, IP-address of the client. Returns none."""
def connection_teardown(sock, addr):
    print("FIN packet is received")
    fin_ack = create_packet(0, 0, FIN | ACK, 15, b'')  # Creating FIN-ACK packet
    sock.sendto(fin_ack, addr)
    print("FIN ACK packet is sent")

"""Description: Function for calculating and displaying throughput of the file transfer.
 Arguments: Start and end time for the transfer, and the total number of bytes received. Returns none."""
def calculate_throughput(start_time, end_time, received_bytes):
    if received_bytes > 0: # Make sure data has actually been received
        elapsed_time = end_time - start_time
        throughput = (received_bytes * 8) / (elapsed_time * 1000000)  # Mbps
        print(f"\nThe throughput is {throughput:.2f} Mbps -- {received_bytes} bytes in {elapsed_time:.2f} seconds")
    else:
        print("Throughput could not be calculated - no data received.")

"""Description: Function for running the server and receive a file with DRTP. Handles packet reception with sequence validation.
Arguments: IP address and port number to bind the server to, and optional packet sequence number to discard. Returns none. """
def run_server(ip, port, discard=None):
    server_socket = socket (AF_INET, SOCK_DGRAM) # Creating a UDP socket
    server_socket.bind((ip, port)) # Binding the address to the socket
    print(f"Server listening on {ip}:{port}")

    # Initializing variables
    expected_seq = 1 # The next expected sequence number
    received_bytes = 0 # Counting total recieved bytes

    try:
        # Connection establishment
        if not three_way_handshake(server_socket):
            print("Connection establishment failed")
            return

        # Data transfer phase
        server_socket.settimeout(None) # Blocking timeout to receive retransmissions
        start_time = time.time() # Used to track total transfer time
        with open("received_file.jpg", "wb") as file: # File for received data
            while True: # Loop for receiving and processing packets
                packet, addr = server_socket.recvfrom(1000)  # 8 bytes header + up to 992 bytes data

                # Separating the header from the data (payload)
                header = packet[:8]
                data = packet[8:]

                # Parsing header and flags
                seq, ack, flags, win = parse_header(header)
                syn, ack, fin = parse_flags(flags)

                # Test case: Discard specific packet
                if discard is not None and seq == discard:
                    print(f"{current_time()} -- packet {seq} is discarded (test case)")
                    discard = None # Only discard once
                    continue # Ignoring packet

                # If FIN-packet is received, close the connection and calculate throughput
                if fin:
                    connection_teardown(server_socket, addr)
                    end_time = time.time()
                    calculate_throughput(start_time, end_time, received_bytes)
                    break

                # If the correct packet is received
                if seq == expected_seq:
                    # Process received data
                    print(f"{current_time()} -- packet {seq} is received")
                    file.write(data) # Writing data to file
                    received_bytes += len(packet) # Updating counter for total recieved bytes, including header-bytes
                    expected_seq += 1 # Updating sequence number for the next expected packet

                    # Acknowledging received data
                    ack_packet = create_packet(0, seq, ACK, 15, b'')
                    server_socket.sendto(ack_packet, addr) # Sending ACK back to client
                    print(f"{current_time()} -- sending ack for the received {seq}")

                # If packet is out-of-order
                else:
                    print(f"{current_time()} -- packet {seq} is out of order and discarded, expected {expected_seq}")
                    continue # Discard without resending ACK

    except Exception as e: # Catching other errors that can occur
        print(f"Server error: {e}")
    finally:
        server_socket.close() # Closing the socket
        print("Connection closes")