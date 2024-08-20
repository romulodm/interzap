# :newspaper: Project Description
<p align="justify ">
This work was carried out in the Computer Networks discipline and aimed to familiarize students with programming network applications using sockets, formalizing a protocol for this. 
In short, we needed to build an application similar to Whatsapp following the protocol specification created by professor Dr. Pedro de Botelho Marcos presented in this <a href="https://docs.google.com/document/d/1HDQIMFCnF1UYwMGFSK9v0luRymGnoUypVbuNAI-cCPQ/edit">link</a>.
</p>

<br>

<div align="center">
  <img align="center" src ="https://github.com/romulodm/interzap/blob/main/inter.png" width ="350" heigth ="100">  
</div>
<p align="center">Figure: Print of what is displayed in the terminal when the client starts</p>

<br>

## :mag_right: Table of Contents

- [Architechture](#architechture)
- [Features](#features)
- [Usage](#usage)

## Architechture

Interzap's architecture is designed to support real-time communication between clients and servers using sockets. Below is an overview of the main components and how they interact:

```
interzap/
│
├── server/                  # Directory containing the server code
│   ├── internal/            # Internal server logic
│   │   ├── chat_server.py   # Main server class that handles requests
│   │   ├── database.py      # Class for managing the SQLite database
│   │   ├── group.py         # Class for managing users in a group
│   │   └── user.py          # Secondary class for handling individual messages in a thread
│   └── main.py              # Script to start the server
│
├── client/                  # Directory containing the client code
│   ├── backup/              # Directory for storing client messages
│   │   ├── Client-000000.py # Example of how messages are stored
│   ├── internal/            # Internal client logic
│   │   ├── chat_client.py   # Main client class
│   │   └── client.py        # Secondary class for managing messages and contacts
│   ├── util/                # Directory for utility functions
│   │   └── convert_posix.py # Functions to convert POSIX timestamps to standard dates
│   └── main.py              # Script to start the client
│
├── README.md                # This file
├── host.py                  # File that defines (or not) the HOST_IP
└── requirements.txt         # Libraries and packages used
```

## Features

:heavy_check_mark: `Login`

:heavy_check_mark: `Register`

:heavy_check_mark: `Send individual message`

:heavy_check_mark: `Send group message`

:heavy_check_mark: `Show whether the message was delivered or read`

:heavy_check_mark: `Save messages from user who is offline (using SQLite)`

:heavy_check_mark: `Save client message history (using .json)`


## Usage
- Run `pip install -r requirements.txt`
- Run `python server/main.py` in the base directory to start the server
- Run `python client/main.py` in the base directory (as many times you want) to open the clients that will consume the server
- Be happy testing on the client 🤠
