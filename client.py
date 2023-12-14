import socket
import pyautogui

MAX_PACKET = 1024
IP = '127.0.0.1'
PORT = 6969
PROTOCOL_SYMBOL = '|'


def protocol(input, mode):
    """
    Format and parse messages based on the protocol.

    :param input: Input message.
    :param mode: 'snd' for sending, 'rcv' for receiving.
    :return: Tuple containing length and message (if applicable).
    """
    if mode == 'snd':
        length_message = len(input)
        message = str(length_message) + PROTOCOL_SYMBOL + input
        print('the message is ' + message)
        return message
    elif mode == 'rcv':
        message_list = input.split(PROTOCOL_SYMBOL)
        assert len(message_list) >= 2, 'Error: invalid message format'
        length_message = message_list[0]
        message = message_list[1]
        assert length_message.isdigit(), 'Error: Length must be a digit.'
        assert int(length_message) == len(message), 'Error: Message length doesnt match specified length.'
        return length_message, message
    else:
        assert False, 'Error: unknown mode'


def send_screenshot():
    """
    Take a screenshot and send it to the server.

    :return: Screenshot bytes.
    """
    try:
        screenshot = pyautogui.screenshot()
        screenshot_bytes = bytearray(screenshot.tobytes())
        assert len(screenshot_bytes) > 0, 'Error: Empty screenshot.'
        print("Screenshot taken.")
        return screenshot_bytes
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None


def disconnect_server(server_socket):
    """
    Disconnect from the server without closing it.

    :param server_socket: Socket connected to the server.
    """
    print('disconnecting from the server...')
    server_socket.close()


def send_screenshot():
    """

    :return:
    """
    try:
        screenshot = pyautogui.screenshot()
        screenshot_bytes = bytearray(screenshot.tobytes())
        return screenshot_bytes
        print("Screenshot sent to the server successfully.")

    except Exception as e:
        print(f"Error taking and sending screenshot: {e}")


def process_command(command, my_socket):
    """
    Process the command entered by the user.

    :param command: Command entered by the user.
    :param my_socket: Socket connected to the server.
    """
    if not command.strip():
        print('Warning: Empty command entered.')
        return
    my_socket.send(protocol(command, 'snd').encode())
    response = my_socket.recv(MAX_PACKET).decode()
    print(response)


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    response = ' '
    try:
        my_socket.connect((IP, PORT))
        while response != '':
            user_input = input('Enter command: ')
            process_command(user_input, my_socket)
    except socket.error as err:
        print(f'Socket error with error code {err}')
    finally:
        disconnect_server(my_socket)
        print('disconnected from the server successfully')


if __name__ == '__main__':
    main()
