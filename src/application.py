import argparse
import ipaddress
from server import run_server
from client import run_client

"""Function for parsing command-line arguments to determine mode (server/client), IP, port, file, etc.
Returns an object containing all parsed arguments"""
def parse_arguments():
    # General arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', action='store_true', help='Run in server mode. Must be run in either client or server.')
    parser.add_argument('-c', '--client', action='store_true', help='Run in client mode. Must be run in either client or server.')
    parser.add_argument('-i', '--ip', default='10.0.1.2', help='Server IP address (IPv4 or IPv6). Defualt is 10.0.1.2.')
    parser.add_argument('-p', '--port', type=int, default=8088, help='Server port number. Defaults is 8088.')

    # Client-specific arguments
    parser.add_argument("-f", "--file", help="File you wish to transfer to the server")
    parser.add_argument("-w", "--window", type=int, default=3, help="Request a window size in client mode. Defaults is 3.")

    # Server specific argument
    parser.add_argument('-d', '--discard', type=int, help="Test case: Discard a spesific packet (specified with the sequence number)")

    return parser.parse_args()

"""Main function that validates arguments and invoke the client or server using parsed command-line inputs
No returns, but exits with appropriate code, 0 for success or 1 for error"""
def main():
    args = parse_arguments() # Parsed arguments

    #Checks if the given IP-address is a valid IPv4 or IPv6 address
    if not ipaddress.ip_address(args.ip):
        print(f"Invalid IP-address: {args.ip}")
        exit(1)

    #Checks if the given port is in valid range
    if not (1025 <= args.port <= 65535):
        print(f"Invalid port: {args.port}. The port number must be in the range (1024, 65535)")
        exit(1)

    try:
        if args.server:
            # Start the server
            run_server(args.ip, args.port, args.discard)
        elif args.client:
            # Start the client
            run_client(args.ip, args.port, args.file, args.window)
        else:
            # If client/server is not specified
            print(f'Error: You need to specify if you want to run in client mode --c or server mode --s')
            exit(1)
    except Exception as e: #Catch all other errors that can occur when trying to run
        print(f'Could not run. Error: {e}')
        exit(1)

    # Exit successfully if completed without any issues
    exit(0)

if __name__ == "__main__":
    main()

