import glob
import os
import datetime
import pyautogui
import subprocess
import shutil
import socket

MAX_PACKET = 1024
QUEUE_LEN = 1
SERVER_NAME = 'coolest server'
PORT = 6969
IP = '127.0.0.1'
COMMAND_LIB = {}
PROTOCOL_SYMBOL = '|'
SAVE_DIRECTORY = r'C:\Users\myrtl\Favorites'


def protocol(user_input, mode):
    """
    Format and parse messages based on the protocol.

    :param user_input: Input message.
    :param mode: 'snd' for sending, 'rcv' for receiving.
    :return: Tuple containing length and message (if applicable).
    """
    if mode == 'snd':
        length_message = len(user_input)
        message = str(length_message) + PROTOCOL_SYMBOL + user_input
        print('the message is ' + message)
        return message
    elif mode == 'rcv':
        message_list = user_input.split(PROTOCOL_SYMBOL)
        assert len(message_list) >= 2, 'Error: invalid message format'
        length_message = message_list[0]
        message = message_list[1]
        assert length_message.isdigit(), 'Error: Length must be a digit.'
        assert int(length_message) == len(message), 'Error: Message length doesnt match specified length.'
        return length_message, message
    else:
        assert False, 'Error: unknown mode'


def list_dir(path):
    """
    List files in the specified directory.

    :param path: Path to the directory.
    :return: List of files.
    """
    assert os.path.exists(path), f"Error: Path '{path}' does not exist."
    files = glob.glob(r'{}\*.*'.format(path))
    files_list = '\n'.join(map(str, files))
    return files_list


def delete_file_or_directory(path):
    """
    Delete a file or directory.

    :param path: Path to the file or directory.
    """
    assert os.path.exists(path), f"Error: Path '{path}' does not exist."
    try:
        path = os.path.normpath(path)
        if os.path.isfile(path):
            os.remove(path)
            print(f"File '{path}' deleted successfully.")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Directory '{path}' and its contents deleted successfully.")
        else:
            print(f"'{path}' is not a valid file or directory.")
    except Exception as e:
        print(f"Error deleting '{path}': {e}")


def copy_file(src_path, dst_path):
    """
    Copy a file from source to destination.

    :param src_path: Source file path.
    :param dst_path: Destination file path.
    """
    assert os.path.isfile(src_path), f"Error: Source file '{src_path}' not found."
    try:
        src_path = os.path.normpath(src_path)
        dst_path = os.path.normpath(dst_path)
        dst_dir = os.path.dirname(dst_path)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        shutil.copy(src_path, dst_path)
        print(f"File '{src_path}' copied to '{dst_path}' successfully.")
    except Exception as e:
        print(f"Error copying file: {e}")


def execute(executable_path):
    """
    Execute an executable.

    :param executable_path: Path to the executable.
    """
    assert os.path.isfile(executable_path), f"Error: Executable file '{executable_path}' not found."
    try:
        executable_path = os.path.normpath(executable_path)
        command = [executable_path]
        return_code = subprocess.call(command)
        print(f"Executable '{executable_path}' executed with return code {return_code}.")
    except Exception as e:
        print(f"Error executing '{executable_path}': {e}")


def receive_and_save_screenshot(client_socket):
    try:
        # Receive the screenshot bytes
        screenshot_bytes = bytearray()
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            screenshot_bytes.extend(data)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.image(screenshot_bytes)
        file_path = os.path.join(SAVE_DIRECTORY, filename)
        screenshot.save(file_path)
        print(f"Screenshot received and saved successfully at: {file_path}")

    except Exception as e:
        print(f"Error receiving and saving screenshot: {e}")


def send_screenshot_back(client_socket, file_name):
    """

    :param client_socket:
    :param file_name:
    :return:
    """
    try:
        with open(SAVE_DIRECTORY + file_name, 'rb') as file:
            screenshot_bytes = file.read()
        client_socket.sendall(screenshot_bytes)
        print("Screenshot sent back to the client successfully.")

    except Exception as e:
        print(f"Error sending screenshot back to the client: {e}")


def connect_to_client(server_socket):
    """

    :param server_socket:
    :return:
    """
    server_socket.bind((IP, PORT))
    server_socket.listen(QUEUE_LEN)
    client_socket, client_address = server_socket.accept()
    return client_socket, client_address


def close_server(server_socket):
    """

    :param server_socket:
    :return:
    """
    print('closing...')
    server_socket.close()
    print('closed server successfully!')


def disconnect_client(client_socket):
    """

    :param client_socket:
    :return:
    """
    print('disconnecting client...')
    client_socket.close()


def process_command(command, client_socket):
    """
    Process the command received from the client.

    :param command: Command received from the client.
    :param client_socket: Socket connected to the client.
    """
    if command.upper() == 'DIR':
        directory = input('Enter directory path to list: ')
        files_list = list_dir(directory)
        response = protocol(files_list, 'snd')
        client_socket.send(response.encode())

    elif command.upper() == 'DELETE':
        path_to_delete = input('Enter file/directory path to delete: ')
        delete_file_or_directory(path_to_delete)
        response = protocol('Deleted successfully', 'snd')
        client_socket.send(response.encode())

    elif command.upper() == 'COPY':
        src_path = input('Enter source file path: ')
        dst_path = input('Enter destination file path: ')
        copy_file(src_path, dst_path)
        response = protocol('Copied successfully', 'snd')
        client_socket.send(response.encode())

    elif command.upper() == 'EXECUTE':
        executable_path = input('Enter path of the executable: ')
        execute(executable_path)
        response = protocol('Executed successfully', 'snd')
        client_socket.send(response.encode())

    elif command.upper() == 'EXIT':
        print('Client disconnected.')
        disconnect_client(client_socket)

    else:
        response = protocol('Invalid command', 'snd')
        client_socket.send(response.encode())


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket, client_address = connect_to_client(server_socket)
        try:
            while True:
                length_input, client_input = protocol(client_socket.recv(MAX_PACKET).decode(), 'rcv')
                print('server received ' + client_input)
                assert length_input.isdigit(), "Error: Length must be a digit."
                assert int(length_input) == len(client_input), "Error: Message length doesn't match specified length."
                process_command(client_input, client_socket)
        except socket.error as err:
            print('received socket error on client socket with error code ' + str(err))
        finally:
            disconnect_client(client_socket)
    except socket.error as err:
        print('received socket error from server with error code ' + str(err))
    finally:
        close_server(server_socket)


if __name__ == '__main__':
    main()
