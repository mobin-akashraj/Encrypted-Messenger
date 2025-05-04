# Encrypted Messenger

- build.py  : Script to build the client executable using PyInstaller.
- server.py : The server-side application that handles client connections and message broadcasting.
- client.py : The client-side application with a graphical user interface.

## How to use:

### Required python libraries:
- customtkinter
- cryptography
- datetime
- pillow

### Running the scripts:

-> Run the server using the command
   + python server.py

-> Run the client using the command
   + python client.py
     + Enter an username update the server's IP and PORT number.

-> To build the .exe file, run the command
   + python build.py
