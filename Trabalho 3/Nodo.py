import socket
import time
import threading

#É setada em True para avisar todas as threads que devem iniciar harakiri.
DEVO_MORRER = False

#Define se o processo é ou não o rei.
KING = 0

#Cria o socket, AF_INET é IPv4.
#sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#O "0"  no luga da porta faz com que o OS escolha uma porta livre por conta própria.
s.bind(("127.0.0.1", 0))

#Retorna uma tupla IP, porta.
MY_PORT = s.getsockname()[1]
print("Estou na porta " + str(MY_PORT))
f = open("port_list.txt", "a")
f.write(str(MY_PORT))
f.close()

#Função que procura pelo rei, enviando mensagens para todas as portas da lista.
def find_the_king():
    global KING
    print("Tentando achar o rei\n")
    f = open("port_list.txt", "r")
    message = "king?"
    for node_port in f:
        s.sendto(message.encode("utf-8"), ("127.0.0.1", int(node_port)))
        for i in range(10):
            print("Tentativa " + str(i) + "...\n")
            try:
                message, address = s.recvfrom(1024)
            except socket.timeout:
                #Continua para próxima tentativa se falhar.                
                continue 
        if data == "sim" and addr == node_port:
            KING = node_port
            break

#Após escrever no arquivo, abre e lê para verificar se a primeira linha escrita é sua própria porta.
f = open("port_list.txt", "r")
lines = f.read()
if str(lines[0].strip("\n")) == str(MY_PORT):
    KING = MY_PORT
    print("I'm king of port", KING)
print(f.read())
f.close()

#Setup inicial do Nodo terminado, temos uma porta e ela está anotada no arquivo de referência.

#################################################################

# Definição das funções que serão rodadas nas threads.
def escutando_mensagem():
    print("escutando...\n")
    while True:
        global DEVO_MORRER
        if DEVO_MORRER == True :
            sair_da_lista()
            break

        #buffer size is 1024 bytes. "data" is the message received, "addr" is the port of the sending process.        
        data, addr = s.recvfrom(1024)
        print ("Mensagem recebida: " + str(data) + "de "+ str(addr) + "\n")

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
         
def sair_da_lista():
    print("Programa fechando")
    global MY_PORT
    #guarda as linhas do arquivo na variável ports_list
    f = open("port_list.txt", "r")

    #Aqui, caso eu usasse o método f.read, port_list receberia uma string inteira, o que é menos prático para iteração que list(f) que retorna uma lista com as linhas do arquivo.
    ports_list = list(f)    
    print("ports list is:\n", ports_list)
    f.close()
    #Usa a variável ports_list pra escrever o arquivo apenas com as portas dos outros nodos.
    f = open("port_list.txt", "w")    
    for node in ports_list:
        print("checking port ", node)
        if node != str(MY_PORT):
            f.write(str(node))
    f.close()

# CHAMANDO THREADS
if __name__ == "__main__":

    #Cria as threads
    escutando_thread = threading.Thread(target=escutando_mensagem, args=())
    enviando_thread = threading.Thread(target=enviando_mensagem, args=())

    #Inicia as threads
    enviando_thread.start()
    escutando_thread.start()
    
    #Faz com que main espere as threads finalizarem antes de fechar.
    #escutando_thread.join()
    #enviando_thread.join()    
