from socket import *
from header import * # Functions for header creation/parsing
from server import current_time # Reuse timestamp from server

"""Description: A three-way handshake with the server to establish a connection. 
Arguments: UDP socket, IP-address and port number for the server, and initial window size proposed by the client.
Returns: The negotiated window size as an integer if success, false otherwise."""
def three_way_handshake(sock, ip, port, sender_window, max_retries=5):
    retry = 0
    sock.settimeout(2) # 2 second timeout per try, in case of packet loss
    syn_packet = create_packet(0, 0, SYN, sender_window, b'') # Creating the SYN packet

    while retry < max_retries: # If packet loss and timeout, retry 5 times
        try:
            #Send SYN
            sock.sendto(syn_packet, (ip, port))
            print("SYN packet is sent")

            #Wait for SYN-ACK
            packet, addr = sock.recvfrom(8)
            seq, ack, flags, win = parse_header(packet)
            syn_flag, ack_flag, fin_flag = parse_flags(flags)
            if syn_flag and ack_flag:
                print("SYN-ACK packet is received")

                #Send ACK
                sending_window = min(sender_window, win)  # Using the smaller of the two windows
                ack_packet = create_packet(0, 0, ACK, sending_window, b'')
                sock.sendto(ack_packet, (ip, port))
                print("ACK packet is sent")
                print("Connection established")
                return sending_window  # Handshake successful

        except timeout:
            retry += 1
            print(f"Timeout waiting for SYN-ACK, retrying... ({retry}/{max_retries})")
    print(f"Connection establishment failed: No response after retries ")
    return False

"""Description: Function for closing the connection, by sending a FIN-packet and waiting for a FIN-ACK back.
Arguments: UDP socket, IP-address and port number for the server. Returns none. """
def connection_teardown(sock, ip, port, max_retries=5):
    print("Connection teardown:")
    fin_pack = create_packet(0, 0, FIN, 0, b'')
    sock.settimeout(3)  # Set timeout for receiving FIN-ACK
    retry = 0
    while retry < max_retries:
        try:
            # Sending FIN
            sock.sendto(fin_pack, (ip, port))
            print("FIN packet is sent")

            #Wait for FIN-ACK
            fin_ack, addr = sock.recvfrom(8)
            seq, ack, flags, win = parse_header(fin_ack)
            syn_flag, ack_flag, fin_flag = parse_flags(flags)

            if ack_flag and fin_flag:
                print("FIN-ACK packet is received")
                print("Connection closes")
                sock.close()
                return
            else:
                print("Unexpected packet during teardown")
        except timeout:
            retry += 1
            print("Timeout waiting for FIN-ACK during teardown")
        except Exception as e:
            retry += 1
            print(f"Error during connection teardown: {e}")
    print("Teardown failed: No FIN-ACK received after maximum retries")
    sock.close()

"""Description: Main client-side function to transfer a file using Go-Back-N.
Arguments: IP-address and port number for the server, path to the file to send, and initial window size. Returns none."""
def run_client (ip, port, file, window):
    try:
        # Read and split file into 992-byte chunks
        with open(file, "rb") as file:
            packets = []
            while True:
                chunk = file.read(992)
                if not chunk:
                    break
                packets.append(chunk)
    except FileNotFoundError: # Error handling if file path is not found
        print(f"File {file} not found.")
        return

    # Initialize UDP socket
    client_socket = socket(AF_INET, SOCK_DGRAM)

    # Connection establishment
    window_size = three_way_handshake(client_socket, ip, port, window)
    if not window_size:
        client_socket.close()
        return

    # Data transfer phase
    base = 1 #Earliest unacknowledged packet in the sliding window, initialized to 1
    next_seq = 1 #The next sequence number to be assigned, initialized to 1
    total_packets = len(packets) #The total number of chunks (packets) that need to be sent

    print("\nData Transfer:")

    # Loop until all packets are acknowledged
    while base <= total_packets:
        # Send all packets in the current window
        while next_seq < base + window_size and next_seq <= total_packets:
            packet = create_packet(next_seq, 0, 0, window_size, packets[next_seq - 1])
            client_socket.sendto(packet, (ip, port))

            # Logging the transmission
            window_contents = list(range(base, min(base + window_size, total_packets + 1))) # Gives a list with the packets in the window
            print(f"{current_time()} -- packet with seq = {next_seq} is sent, sliding window = {window_contents}")

            next_seq += 1

        # Wait for ACK
        try:
            client_socket.settimeout(0.4)  # 400ms timeout for retransmission
            ack_packet, addr = client_socket.recvfrom(8)
            seq, ack, flags, win = parse_header(ack_packet)
            syn_flag, ack_flag, fin_flag = parse_flags(flags)
            if ack_flag and ack >= base: # If ACK is correct and in the current window (not a duplicate)
                    print(f"{current_time()} -- ACK for packet = {ack} is received")
                    base = ack + 1  # Slide window forward
        except timeout: # Retransmission timeout
            print(f"{current_time()} -- RTO occured")
            next_seq = base  # Reset to base for Go-Back-N retransmission
            for seq in range(base, min(base + window_size, total_packets + 1)):
                print(f"{current_time()} -- Retransmitting packet with seq = {seq}")
            continue # Packets are retransmitted in the main loop
    print("Data finished")

    # Connection teardown phase
    connection_teardown(client_socket, ip, port)

