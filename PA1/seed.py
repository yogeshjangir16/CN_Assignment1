import socket
import threading

#intialize ip address, port number and peer list for listing
MY_IP = "127.0.0.1"                                                
PORT = int(input("Enter Port Number: "))                                                    
peer_list = []                                                         


#Output file where all output seed will be store
def Output_File(output):
    try:
        file = open("outputseed.txt", "a")  
        file.write(output + "\n") 
    except:
        print("Write Failed")
    finally:
        file.close()

#Connection Creation to connect multiple devices
def Creation_Server():
    try:
        global socket
        socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except:
        print("Try Again!!! Error In Socket Creation")

def Socket_Binding_fxn(): # Bind the socket
    try:
        global socket
        ADDRESS = (MY_IP, PORT)
        socket.bind(ADDRESS)
    except:
        print("Try Again!!! Error In Socket Binding")
        Socket_Binding_fxn()

def convert_string_fxn(peer_list):   # Convert Connected peer Msg to string for sending the socket
    PeerList = ","  
    for i in peer_list:  
        PeerList += i + ","    
    return PeerList  

def Dead_Node_Remove(data): # Print the dead msg and then store it address and remove this address from peer list
    print(data)
    Output_File(data)
    data = data.split(":")
    dead_node = str(data[1]) + ":" + str(data[2])
    if dead_node in peer_list:
        peer_list.remove(dead_node)

def Handle_Peer_Fxn(Connection, Addresss): # Receive peer address from peer and store into peer list.
    while True:
        try:
            data = Connection.recv(1024).decode('utf-8')   # Receive data from peer and decode it   
            if data:
                if "Dead Node" in data[0:9]:# If data indicates a dead node then remove
                    Dead_Node_Remove(data)
                else:
                    data = data.split(":")  # Split data by ":" and append to peer list
                    peer_list.append(str(Addresss[0])+":"+str(data[1]))
                    output = "Received Connection from " + str(Addresss[0])+":"+str(data[1])
                    print(output)
                    Output_File(output)
                    PeerList = convert_string_fxn(peer_list)
                    Connection.send(PeerList.encode('utf-8'))  # Send updated peer list to peer
        except Exception as e:
            print("Exception in handling in peer : ", e)
            break
    Connection.close()


def Server_Begin():
    socket.listen(5) # Start listening for connections
    print("Seed is Listening")
    # Loop to continuously accept new connections
    while True:
        conn, addr = socket.accept()
        socket.setblocking(1) 
        # Create new thread for handling connection
        thread = threading.Thread(target=Handle_Peer_Fxn, args=(conn,addr))
        thread.start()
        
Creation_Server()
Socket_Binding_fxn()
Server_Begin()