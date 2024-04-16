import socket
### Some global settings/variables used
lnbr = "\r\n"
IP = "127.0.0.1"
UDP_PORT = 8089 # iMotions external API
# iMotions parameters
# send external API message (mouseEvent or slideChangeEvent)
def sendup(message):
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.sendto(bytes(message,"utf-8"),(IP,UDP_PORT))
    #log.write("ExtAPI message sent: " + message)

def changeEvent(name,end):
# discrete header
# version 2
    header = "M;2;"
#field 5: slideID
#field 7: marker type N
# (marks the start of the next segment, automatically closing any currently
# open segment.)
    if end==1:
        event = ";;" + name + ";;E;"
    if end ==0:
        event = ";;" + name + ";;S;V"
    return header + event + lnbr