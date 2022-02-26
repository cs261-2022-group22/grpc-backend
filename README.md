# gRPC Backend

> ### Original Author:
> Varun Chodanker
> ### Disclaimer:
> This is written according to my interpretation of gRPC. As I have no experience with gRPC prior to this project, there may be errors contained within this document. Please see [https://grpc.io/docs/](https://grpc.io/docs/) for the official documentation which should serve as the canonical source regarding this topic.

## Project File Sturcture

```
common/                     # The Git submodule, holding common proto files
compiled_protos/            # Where the compiled protobuf files are located
services/                   # Directory for each microservices
   ...  /*Service.py        # Service wrapper code, contains the gRPC class wrapper and the
                            # begin/endServe functions.
   ...  /*ServiceImpl.py    # Service implementation code, the actual logic being executed is here
                            # "Impl" for Implementation.

*_server.py                 # The entry point of each service.
```

## gRPC

- gRPC defines services. These services provide remote procedural calls (RPCs). A server corresponds to a particular service and implements its RPCs so that clients can send call requests for these and receive responses. For each RPC, the request and response type is declared. This specifies the parameters of the call requests, from the client, and the variables that are returned in responses, from the server. Services are defined with **`.proto`** files. gRPC
is beneficial due to its high performance.

## [BetterProto](https://github.com/danielgtaylor/python-betterproto)

It's a drop-in replacement of Google's protobuf library, it provides:

- Better type-hinting
- Cleaner generated source files.
- and finally, async support (but trapped by an upstream Python bug)

The generated code goes to `compiled_protos/`, as stated below:

## Python gRPC Server

- See [gRPC QuickStart](https://grpc.io/docs/languages/python/quickstart/) for how supporting code files are generated. This also illustrates how Python gRPC servers are built.
- Don't forget to install required dependencies before going on, install them by running:
    - `pip install -r ./requirements.txt`
- The supporting code is generated from the root directory of the project by using the following command:
    - `python -m grpc_tools.protoc -I./common/ --python_betterproto_out=./compiled_protos/ ./common/*.proto`
- Create a virtual environment according to requirements.txt and activate it.
    - See [Creating Virtual Environments](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-virtual-environments).
- Start the the server so that the gRPC calls, of its corresponding service, can be serviced.  
    - `python <service_name>_server.py`
- Hit Ctrl-C to stop the server.

## Node.js Javascript GRPC Client

- See [https://grpc.io/docs/languages/node/quickstart/](https://grpc.io/docs/languages/node/quickstart/) for how Node gRPC clients are built.
- Install dependencies according to **package.json**.  
`npm install`
- After ensuring the server is already running, run the client. It will make gRPC calls requests that are received by the server. The server runs these and returns a response. The client can perform appropriate actions based on the response.  
`node <filename>`

## PostgreSQL Database

- A PostgreSQL database according to **[schema.sql](https://github.com/cs261-2022-group22/postgresql-schema/blob/main/schema.sql)** is utilised for the data persistence of the application.
- The environment variables **`POSTGRES_DATABASE`**, **`POSTGRES_USER`**, **`POSTGRES_PASSWORD`**, **`POSTGRES_HOST`**, **`POSTGRES_PORT`** should be set or provided in an **.env** file in the root directory of the project.
    - See [https://12factor.net/config](https://12factor.net/config) and [https://pypi.org/project/python-dotenv/](https://pypi.org/project/python-dotenv/).  
    - These environment variables provide the parameters for a connection to a conforming database. See [https://www.psycopg.org/docs/module.html](https://www.psycopg.org/docs/module.html).

## Password Handling

- The passwords of accounts are hashed with salts before being stored in the database. Then, passwords are compared with the hashes to check that they match.
- In **Python**, *bcrypt* is used to generate the salt and hash the password with it. Then it is also used to check whether a given password matches with the stored hash - to allow the user to be logged in. See <https://pypi.org/project/bcrypt/> and <https://docs.python.org/3/library/stdtypes.html>.
