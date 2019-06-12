import socket
import time
import threading
from asyncio import Semaphore

# É setada em True para avisar todas as threads que devem iniciar harakiri.
DEVO_MORRER = False

# Identificação do rei
KING_ID = -1
KING_CHECKED = False
WAITING_KING = False
KING_SEMAPHORE = Semaphore(0)

MSG_VIVO = 'VIVO'
MSG_VIVO_OK = 'VIVO_OK'
MSG_CLOSE = 'CLOSE'


# Cria o socket, AF_INET é IPv4.
# sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# O "0"  no luga da porta faz com que o OS escolha uma porta livre por conta própria.
s.bind(("127.0.0.1", 0))

#Retorna uma tupla IP, porta, o índice pega só a porta.
MY_PORT = s.getsockname()[1]
print("Estou na porta " + str(MY_PORT))
f = open("port_list.txt", "a")
f.write(str(MY_PORT) + "\n")
f.close()        

#Após escrever no arquivo, abre e lê para verificar se a primeira linha escrita é sua própria porta.
f = open("port_list.txt", "r")
ports_list = list(f)
# Primeiro rei é o primeiro a escrever
KING_ID = int(ports_list[0])
print("The king is", KING_ID)

print(f.read())
f.close()

#Setup inicial do Nodo terminado, temos uma porta e ela está anotada no arquivo de referência.

#################################################################

# Definição das funções que serão rodadas nas threads.
def thread_que_verifica_king():

    global KING_ID
    global KING_CHECKED
    global MSG_VIVO
    global WAITING_KING
    
    while not(DEVO_MORRER):

        KING_CHECKED = False
        WAITING_KING = True
        print("Tentando verificar o rei\n")
        enviar_mensagem(MSG_VIVO, node_port = KING_ID)

        time.sleep(8)

        if(not(KING_CHECKED)):
            print("The king is dead!!\nAnarchy! ")
            break
            #KING_SEMAPHORE.acquire()

def thread_escuta_mensangens():
    print("escutando...\n")

    global DEVO_MORRER
    global WAITING_KING
    global KING_CHECKED
    global KING_ID

    while not(DEVO_MORRER):
        
        #buffer size is 1024 bytes. "data" is the message received, "addr" is the address of the sending process.       
        try: 
            data, addr = s.recvfrom(1024)
            addr_port = addr[1]
            message = data.decode("utf-8") 

            print ("Mensagem recebida: " + message + " de "+ str(addr) + "\n")

            if(message == MSG_VIVO ):
                enviar_mensagem(MSG_VIVO_OK, node_port = addr_port)

            elif(message == MSG_VIVO_OK and addr_port == KING_ID and WAITING_KING):
                KING_CHECKED = True
                WAITING_KING = False

            elif(message == MSG_CLOSE):
                DEVO_MORRER = True
                sair_da_lista()
        except:
            pass


def thread_interface():

    global DEVO_MORRER
    global MSG_CLOSE

    while not(DEVO_MORRER):

        message = input("O que devo fazer? ")
        message = message.replace(' ','')

        enviar_mensagem(message, broadcast = True)
        time.sleep(0.2)


#Definição das funções que serão chamadas dentro do programa
    #Funções que serão chamadas pela interface.
def get_king():
    if (not WAITING_KING):
        print("O atual rei é: " + str(KING_ID) + "\n")
        print("Longa vida ao rei!\n")
    else:
        print("Nosso rei foi decapitado, voltao daqui a pouco.\n")
        print("Não fui eu que decapitei ok?\n")

def enviar_mensagem(message, node_port=-1, broadcast = False): 

    try:

        if(broadcast):
            #opens the ports file with the "r" option, read_only.
            f = open("port_list.txt", "r")
            ports = list(f)
            #iterates over every line in the file. For python each line works as an element in an array.
            for node in ports:
                s.sendto(message.encode("utf-8"), ("127.0.0.1", int(node)))
                print ("Mensagem enviada: " + str(message) + " para todos os nós"+ "\n")
            f.close()

        else:
            s.sendto(message.encode("utf-8"), ("127.0.0.1", int(node_port)))
            print ("Mensagem enviada: " + str(message) + " para "+ str(node_port) + "\n")
    except:
        if(broadcast):
            print("Ocorreu um erro ao enviar " + message+" para o nó "+str(node_port))
        else:
            print("Ocorreu um erro ao enviar " + message+" em broadcast")


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
        print("removing port ", node)
        if node != str(MY_PORT) + "\n":
            f.write(str(node))
    f.close()

# CHAMANDO THREADS
if __name__ == "__main__":

    #Cria as threads

    # Thread responsável por receber mensagens e tomar ações.
    thread_escuta_mensangens = threading.Thread(target=thread_escuta_mensangens, args=())

    # Thread responsável por gerenciar interface com usuário
    thread_interface = threading.Thread(target=thread_interface, args=())

    # Thread responsável em detectar a presença do líder
    thread_que_verifica_king = threading.Thread(target=thread_que_verifica_king, args=())


    #Inicia as threads
    thread_interface.start()
    thread_escuta_mensangens.start()
    thread_que_verifica_king.start()
    
    #Faz com que main espere as threads finalizarem antes de fechar.
    thread_interface.join()

    message = input("Saindo.. Pressione enter para continuar... ")
