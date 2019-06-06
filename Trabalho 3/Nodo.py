import socket
import time
import threading

#Cria o socket, AF_INET é IPv4.
#sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#gethostname() seta o ip do socket como sendo o ip da máquina local (127.0.0.1). O "0" faz com que o OS escolha uma porta livre por conta própria.
s.bind(("127.0.0.1", 0)) 
#Retorna uma tupla IP, porta.
port = s.getsockname()[1]
print("esta é a porta " + str(port))
f = open("port_list.txt", "a")
f.write(str(port) + '\n')
f.close()
DEVO_MORRER = False
f = open("port_list.txt", "r")
print(f.read())
f.close()

#Setup inicial do Nodo terminado, temos uma porta e ela está anotada no arquivo de referência.
def escutando_mensagem():
    print("escutando...\n")
    while True:
        global DEVO_MORRER
        if DEVO_MORRER == True :
            break
        #buffer size is 1024 bytes. "data" is the message received, "addr" is the port of the sending process.        
        data, addr = s.recvfrom(1024)
        print ("\nMensagem recebida: " + str(data) + "de "+ str(addr) + "\n")     
        print("O que devo fazer?\n")
def enviando_mensagem():    
    while True:
        global DEVO_MORRER
        if DEVO_MORRER == True :
            break
        time.sleep(0.2)
        message = input("O que devo fazer? ")
        #Closes process if the message received was close.
        if message == "close":
            DEVO_MORRER = True
        #opens the ports file with the "r" option, read_only.
        ports = open("port_list.txt", "r")
        #iterates over every line in the file. For python each line works as an element in an array.
        for node_port in ports:            
            s.sendto(message.encode("utf-8"), ("127.0.0.1", int(node_port))) 
            print("Mensagem enviada para " + node_port)        
         
# CHAMANDO THREADS
if __name__ == "__main__":
    #Cria as threads
    escutando_thread = threading.Thread(target=escutando_mensagem, args=())
    enviando_thread = threading.Thread(target=enviando_mensagem, args=())
    #Inicia as threads
    enviando_thread.start()
    escutando_thread.start()
    
    #Faz com que main espere as threads finalzarem antes de fechar.
    #escutando_thread.join()
    #enviando_thread.join()
