# MASTER THESIS
Repository hosting the master thesis project.

### DIRECTORIES CONTENT:

#### offloading_architecture:
Contains the files for the offloading mechanism and the protocol definition (protobuf subdirectory).  All these files are far from complete, they are a preliminary test to familiarize with ryu and test the protocol.

_client.py_ --> test of how the client (mobile edge device) should use the protocol to communicate to the offloading server  
_edge_server.py_ --> test of how the edge server should use the protocol to receive the offloading requests (almost same content of offloading_server.py)  
_msg_handler.py_ --> ryu module that runs on the offloading server responsible of receiving the request from the clients and create new flow request  
_msg_receiver.py_ --> ryu module responsible of receiving the new flow requests and their installation (INCOMPLETE). The communication between this module and msg_handler is supposed to happen through ryu events, but it doesn't work  
_offloading_server.py_ --> test of the protocol messages on the server side

_./protobuf/messages.proto_ --> google protobuf files containing the message definition  
_./protobuf/messages_pb2.py_ --> compiled version of the messages


#### project:
Contains all the files for the path prediction system, including the mininet topology, the packet counter, the script to build the dataset from the capture file, the script to train the LSTM and the different evaluation.

The dataset is built by combining the packet counter and the routing table in each run with the script _pair_dataset.py_. The capture files and the routing tables are in the __DATASET_DIR__ folder, the script pairs the information and save it in __DATASET_DIR__, saving the dataset for each target. Both the scripts contain the variable __DATASET_DIR__ that needs to have the same value.

The topology used for the dataset generation is in _topology.py_, to start the network for the dataset generation run _start.py_. To create the files necessary for the dataset, you also need to start the ryu app the retrieves the packet counter **switchWithStats.py**.

To generate the dataset, after setting the parameters in the two scripts to the desired values, run in separate shell:

`ryu-manager switchWithStats.py`  
`sudo python start.py`  

__NOTE__:  
Some commit dates could be wrong because of problem with time synch on the VM
