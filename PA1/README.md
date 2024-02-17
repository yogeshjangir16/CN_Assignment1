Name : Yogesh Jangir (B21CS083) And G Mukund (B21CS092)

Seed:
1. Establish a connection, bind the connection, and listen for requests and messages.
2. After a peer connect request, it creates a separate thread.
3. Send a peer's request for a connection together with its peer list.
4. It will remove unwanted communications from its list of peers.

Peer:
1. Connect to seed file
2. Requst to seed
3. Randomly connect with a few peers from list
4. Creates threads for listening, Goship, and Liveness
5. Liveness requests and gossip messages can be forwarded.
6. Seed node receives dead node warning for down peers.

Compilation:
1. In config.txt file include IP address and port number And both and be indetify by ":", (example : 172.30.21.114:8000 IP = 172.30.21.114 and Port = 8000)
2. Compile seed node by using py -3.11 seed.py
- Run seeds with different port numbers based on config file entries. Only enter port NO. (In my file we have only 8000,8002,8004,8006,8008)
3. Complie Peer node by using py -3.11 peer.py
- Give port number what we want and check that it's different from peer port number.
- for generate many peer we can repeat above steps.

