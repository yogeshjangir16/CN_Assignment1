import socket
import threading
import time
import hashlib
import random
from queue import Queue

# Number of thread = 3 (Goship, listen, liveness)
count_thread = 3 
Job_Number = [1, 2, 3] # Three job for running each thread one by one
queue = Queue() # Store all the jobs

IP_ADDRESS = "127.0.0.1"
PORT = int(input("Enter Port Number: "))
seeds_addr = set() # Store seed address
PEER_SEED = set() # Store Different Peer address
CONNECTED_PEER = [] # Connected Peer Address
MSG_ARRAY = [] # Hash of goship Message
SEED_ADDRESS = [] # seed address that connected with peer


# Output file for store all peer address output
def Output_File(output):
    try:
        with open("outputpeer.txt", "a") as f:
            f.write(output + "\n")
    except Exception as e:
        print("Write Failed:", e)

class Peer: # Peer Object
    i = 0
    address = ""
    def __init__(self, addr):
        self.address = addr


def Hash_Msg(message): # Generate hash Message
    return hashlib.sha256(message.encode()).hexdigest()


def timestamp():
    return time.time()


def Seed_Read_Fxn(): # Read Address of seed from config
    try:
        global seed_List
        with open("config.txt", "r") as file:
            seed_List = file.read()
    except Exception as e:
        print("Error in config", e)


def Count_Seed(): # Count All availble Seed
    global seed_List
    count = 0
    for line in seed_List.split("\n"):
         if line:
            parts = line.split(":")
            if len(parts) > 1:
                seed_addr = "127.0.0.1:" + str(parts[1])
                seeds_addr.add(seed_addr)
                count += 1
    return count

def Random_Generator(s_min, s_max, k): # Generate K random number beacuse K = floor (n/2) + 1
    temp = set()
    while len(temp) < k:
        temp.add(random.randint(s_min, s_max))
    return temp


def Socket_Creation(): # Connection Esatablished
    try:
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Try Again!!! Error In Socket Creation")

def Socket_Binding_Fxn(): # Bind the socket
    try:
        global sock
        ADDRESS = (IP_ADDRESS, PORT)
        sock.bind(ADDRESS)
    except socket.error:
        print("Try Again!!! Error In Socket Binding")
        Socket_Binding_Fxn()

# Handle linked peers in separate threads.It receives peer communications.
# If a new connection request is made, verify if 4 peers are not connected and accept.
# Return liveness if requested.  
# If not in ML list, forward gossip message.
def Handle_Connected_Peer(Connection, addr):
    while True:
        try:
            msg = Connection.recv(1024).decode('utf-8')
            received_data = msg

            if not msg:
                break

            data = msg.split(":")

            if "New Connection Request" in data[0]:
                if len(CONNECTED_PEER) < 4:
                    Connection.send("New Connection Accepted".encode('utf-8'))
                    CONNECTED_PEER.append(Peer(f"{addr[0]}:{data[2]}"))

            elif "Liveness Request" in data[0]:
                liveness_reply = f"Liveness Reply:{data[1]}:{data[2]}:127.0.0.1"
                Connection.send(liveness_reply.encode('utf-8'))

            elif "GOSSIP" in data[3][0:6]:
                Goship_Message_Fxn(received_data)

        except Exception as e:
            print(f"Error handling connection with {addr}: {e}")
            break

    Connection.close()

# Listen to a port and create threads for peers  
def Server_Begin(): 
    sock.listen(5)
    print("Active Peer")
    while True:
        conn, addr = sock.accept()
        sock.setblocking(1)
        thread = threading.Thread(target=Handle_Connected_Peer, args=(conn, addr))
        thread.start()

# connects peers from a complete list and random index.
def Connect_Peer_Fxn(CPL, nodes):
    for i in nodes:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_addr = CPL[i].split(":")
            ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
            sock.connect(ADDRESS)
            
            CONNECTED_PEER.append(Peer(CPL[i]))
            
            data = "New Connect Request From:" + str(IP_ADDRESS) + ":" + str(PORT)
            sock.send(data.encode('utf-8'))
            
            received_data = sock.recv(1024).decode('utf-8')
            print(received_data)
            
            sock.close()
        
        except Exception as e:
            print("Peer Connection Error:", e)


# This method takes a whole list of peers and generates a random set of that size to connect to 1 and 4.  
# Since we want to connect to at most 4 random peers, we choose a random number between 1 and 4.
def Join_Nodes(CPL):
    if len(CPL) > 0:
        limit = min(random.randint(1, len(CPL)), 4)
        nodes = Random_Generator(0, len(
            CPL) - 1, limit) 
        Connect_Peer_Fxn(CPL, nodes)

# It unites each seed's peer list separated by comma.
def Peer_List_Addition_Fxn(CPL):
    global IP_ADDRESS
    if not CPL:
        print("Error: No peers in the list.")
        return []
    CPL = CPL.split(",")
    if not CPL:
        print("Error: No peers in the list after splitting.")
        return []
    IP_ADDRESS = CPL[-1].split(":")[0]
    CPL.pop()  
    return CPL

# We connect to seed, submit our IP address and port details, and receive a list of peers connected to seed separated by comma.
# Call join_atmost_4_peers to connect to atmost peers after detecting union.
def Seed_Connection_Fxn(CPL, IP_ADDRESS):
    for i in range(0, len(SEED_ADDRESS)):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_addr = SEED_ADDRESS[i].split(":")
            ADDRESS = (str(seed_addr[0]), int(seed_addr[1]))
            print(ADDRESS)
            sock.connect(ADDRESS)
            MY_ADDRESS = str(IP_ADDRESS)+":"+str(PORT)
            sock.send(MY_ADDRESS.encode('utf-8'))
            data = sock.recv(10240).decode('utf-8')
            CPL = Peer_List_Addition_Fxn(data)
            for peer in CPL:
                print(peer)
                Output_File(peer)
            sock.close()
        except Exception as e:
            print("Seed Connection Error", e)
    Join_Nodes(CPL)

# registers peers to (floor(n / 2) + 1) random seeds.
def Connect_K_seed():  
    global seeds_addr
    seeds_addr = list(seeds_addr)
    seed_nodes_index = Random_Generator(0, n - 1, n // 2 + 1)
    seed_nodes_index = list(seed_nodes_index)
    for i in seed_nodes_index:
        SEED_ADDRESS.append(seeds_addr[i])
    CPL = "" 
    CPL = Peer_List_Addition_Fxn(CPL)

    Seed_Connection_Fxn(CPL, IP_ADDRESS)

# retrieves downed peer address. Notify all associated seeds of dead node.
def Dead_Node(peer):
    dead_msg_data = "Dead Node:" + peer + ":" + \
        str(timestamp()) + ":" + "127.0.0.1"
    print(dead_msg_data)
    Output_File(dead_msg_data)
    for seed in SEED_ADDRESS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            seed_address = seed.split(":")
            ADDRESS = (str(seed_address[0]), int(seed_address[1]))
            sock.connect(ADDRESS)
            sock.send(dead_msg_data.encode('utf-8'))
            sock.close()
        except:
            print("Seed Down ", seed)

# This function sends liveness requests to all connected peers every 13 seconds.
# Report dead if three replies are missing.
# Start from 0 again if it sends liveness req and gets reply to check for 3 consecutive failures.
# Count 3 consecutive connection failures for a peer.
# Report this peer as dead and delete from connected peers list after three failures.
def Liveness_Request_Fxn():
    while True:
        liveness_request = "Liveness Request:" + \
            str(timestamp()) + ":" + "127.0.0.1"
        print(liveness_request)
        for peer in CONNECTED_PEER:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_addr = peer.address.split(":")
                ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
                sock.connect(ADDRESS)
                sock.send(liveness_request.encode('utf-8'))
                print(sock.recv(1024).decode('utf-8'))
                sock.close()
                peer.i = 0           
            except:                     
                peer.i = peer.i + 1
                if (peer.i == 3):
                    Dead_Node(peer.address)
                    CONNECTED_PEER.remove(peer)
        time.sleep(13)

# To minimize flooding/looping, forward gossip messages to linked peers if their hash is not in Message List. 
# if hash msg is already in list then not forward
# forward gossip message to all connected peers
def Goship_Message_Fxn(received_message):
    hash = Hash_Msg(received_message)
    if hash in MSG_ARRAY:       
        pass
    else:
        MSG_ARRAY.append(str(hash))
        print(received_message)
        Output_File(received_message)
        for peer in CONNECTED_PEER:     
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_addr = peer.address.split(":")
                ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
                sock.connect(ADDRESS)
                sock.send(received_message.encode('utf-8'))
                sock.close()
            except:
                continue

# Generate goship msg and sent to connected peer
def Send_Goship_Msg(i):
    g_msg_data = str(timestamp()) + ":" + "127.0.0.1" + \
        ":" + str(PORT) + ":" + "GOSSIP" + str(i+1)
    MSG_ARRAY.append(str(Hash_Msg(g_msg_data)))
    for peer in CONNECTED_PEER:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_addr = peer.address.split(":")
            ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
            sock.connect(ADDRESS)
            sock.send(g_msg_data.encode('utf-8'))
            sock.close()
        except:
            print("Peer Down ", peer.address)


# Generate 10 goship msg interval of 5sed
def gossip():
    for i in range(10):
        Send_Goship_Msg(i)
        time.sleep(5)


def Work_Creation():
    for _ in range(count_thread):
        thread = threading.Thread(target=work)
        thread.daemon = True
        thread.start()
        
def work():
    while True:
        temp = queue.get()
        if temp == 1:
            Socket_Creation()
            Socket_Binding_Fxn()
            Server_Begin()
        elif temp == 2:
            Liveness_Request_Fxn()
        elif temp == 3:
            gossip()
        queue.task_done()
def Job_Creation():
    for i in Job_Number:
        queue.put(i)
    queue.join()


Seed_Read_Fxn()
n = Count_Seed()
Connect_K_seed()                       
Work_Creation()
Job_Creation()
