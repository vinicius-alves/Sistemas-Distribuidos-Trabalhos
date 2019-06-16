import socket
import time
import threading

                        #########SETUP INICIAL###########

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
print("Presentes portas são: " + f.read())
f.close()

# É setada em True para avisar todas as threads que devem iniciar harakiri.
DEVO_MORRER = False
FINGINDO_MORTO = False

# Identificação do rei
KING_ID = int(ports_list[0])
KING_CHECKED = False
WAITING_KING = False
KING_SEMAPHORE = threading.BoundedSemaphore(1)
print("The king is", KING_ID)

# Eleição
# Minha eleição está ocorrendo ou outra eleição de um nó com maior ID está ocorrendo.
MINHA_ELEICAO = False
OUTRA_ELEICAO_COM_MAIOR_ID = False

#Definição das mensagens que serão recebidas pela thread que escuta mensagens.
MSG_VIVO    = "VIVO"
MSG_VIVO_OK = "VIVO_OK"
MSG_CLOSE   = "CLOSE"
MSG_ELEICAO = "ELEICAO"
MSG_OK      = "OK"
MSG_COORDENADOR = "COORDENADOR"

#Armazenamento do número de mensagens enviadas e recebidas de  cada tipo.
QTD_ENV_VIVO = 0
QTD_ENV_VIVO_OK = 0
QTD_ENV_ELEICAO = 0
QTD_ENV_COORDENADOR = 0
QTD_ENV_OK = 0

QTD_REC_VIVO = 0
QTD_REC_VIVO_OK = 0
QTD_REC_ELEICAO = 0
QTD_REC_COORDENADOR = 0
QTD_REC_OK = 0

#Setup inicial do Nodo terminado, temos uma porta e ela está anotada no arquivo de referência.

#################################################################

# Definição das funções que serão rodadas nas threads.
def thread_que_verifica_king():

    global KING_ID
    global KING_CHECKED
    global KING_SEMAPHORE
    global MSG_VIVO
    global WAITING_KING
    global QTD_ENV_VIVO
    global MINHA_ELEICAO
    global FINGINDO_MORTO

    while not(DEVO_MORRER):

        KING_CHECKED = False
        WAITING_KING = True
        print("Tentando verificar o rei\n")
        QTD_ENV_VIVO += 1
        enviar_mensagem(MSG_VIVO, node_port = KING_ID)

        time.sleep(8)

        if(not(KING_CHECKED) and not(FINGINDO_MORTO)):
            print("The king is dead!!\nAnarchy! ")
            iniciar_eleicao()
            KING_SEMAPHORE.acquire(True)
    print("Thread de verificação do rei saindo")


def thread_escuta_mensangens():
    print("\nescutando...\n")
    global FINGINDO_MORTO
    global DEVO_MORRER
    global WAITING_KING
    global KING_CHECKED
    global KING_ID
    global KING_SEMAPHORE
    global MINHA_ELEICAO
    global OUTRA_ELEICAO_COM_MAIOR_ID

    global MSG_CLOSE
    global MSG_ELEICAO
    global MSG_COORDENADOR
    global MSG_OK
    global MSG_VIVO
    global MSG_VIVO_OK

    global QTD_ENV_VIVO_OK

    global QTD_REC_VIVO
    global QTD_REC_COORDENADOR
    global QTD_REC_VIVO_OK
    global QTD_REC_ELEICAO
    global QTD_ENV_OK

    while (not DEVO_MORRER):        
        #buffer size is 1024 bytes. "data" is the message received, "addr" is the address of the sending process, which is a tuple (ip, port).
        try: 
            data, addr = s.recvfrom(1024)
            addr_port = addr[1]
            message = data.decode("utf-8") 

            print ("Mensagem recebida: " + message + " de "+ str(addr) + "\n")

            if(message == MSG_VIVO):
                QTD_REC_VIVO += 1
                if (not FINGINDO_MORTO):
                    enviar_mensagem(MSG_VIVO_OK, node_port = addr_port)
                    QTD_ENV_VIVO_OK += 1
            
            elif(message == MSG_VIVO_OK and addr_port == KING_ID and WAITING_KING):
                QTD_REC_VIVO_OK += 1
                KING_CHECKED = True
                WAITING_KING = False

            elif(message == MSG_CLOSE):
                DEVO_MORRER = True
                sair_da_lista()
                break
            elif(message == MSG_ELEICAO):
                QTD_REC_ELEICAO += 1
                if (MY_PORT > addr_port and not(FINGINDO_MORTO)):
                    QTD_ENV_OK += 1
                    enviar_mensagem(MSG_OK, node_port = addr_port)
                else:
                    OUTRA_ELEICAO_COM_MAIOR_ID = True

            elif(message == MSG_COORDENADOR):
                QTD_REC_COORDENADOR += 1
                OUTRA_ELEICAO_COM_MAIOR_ID = False
                KING_ID = addr_port
                KING_SEMAPHORE.release()

            elif(message == MSG_OK):
                MINHA_ELEICAO = False

        except:
            pass
    print("Thread de escuta saindo")

'''
Comandos da Interface:

close => encerra o processo do nó.
terminar => encerra todos os nós.
falhar => falha o nó, que para de responder mensagens dos outros nós.
recuperar => faz o no voltar a responder mensagens.
dados => imprime um relatório com todos os dados.

'''

def thread_interface():

    global DEVO_MORRER
    global MSG_CLOSE
    global RELATORIO
    while not(DEVO_MORRER):

        message = input("O que devo fazer? ")
        message = message.replace(' ','')
        message = message.lower()

        if (message == "close"):
            message = message.replace("close", MSG_CLOSE)
            enviar_mensagem(message, node_port = MY_PORT)
            sair_da_lista()
        # Aqui, como substituo o comando que chega pelo input pela mensagem que vai ser realmente broadcastada, 
        # guardada numa variável global, fico livre pra troca essa mensagem pela que eu quiser, se no futuro eu perceber que
        # é necessário que todas mensagens broadcastadas tenham o mesmo tamanho.
        if (message == "terminar"): 
            message = message.replace("terminar", MSG_CLOSE)
            enviar_mensagem(message, broadcast = True)
        if (message == "rei"):
            get_king()
            #print("O atual rei é: " + str(KING_ID) + "\n")
        if (message == "falhar"):
            FINGINDO_MORTO = True
        if (message == "recuperar"):
            FINGINDO_MORTO = False
        if (message == "dados"):
            imprimir_relatorio()
        time.sleep(0.2)
    print("Thread de interface saindo")
    
#Definição das funções que serão chamadas dentro do programa
    #Funções que serão chamadas pela interface.
def get_king():
    if (not WAITING_KING):
        print("O atual rei é: " + str(KING_ID) + "\n")
        print("Longa vida ao rei!\n")
    else:
        print("Nosso rei foi decapitado, estamos escolhendo outro.\n")
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
            f.close()

            print ("Mensagem enviada: " + str(message) + " para todos os nós"+ "\n")

        else:
            s.sendto(message.encode("utf-8"), ("127.0.0.1", int(node_port)))
            print ("Mensagem enviada: " + str(message) + " para "+ str(node_port) + "\n")
    except:
        if(broadcast):
            print("Ocorreu um erro ao enviar " + message+" em broadcast")
        else:
            print("Ocorreu um erro ao enviar " + message+" para o nó "+str(node_port))

    #Funções que serão chamadas pela thread que verifica o rei.

def iniciar_eleicao():
    global MINHA_ELEICAO
    global OUTRA_ELEICAO_COM_MAIOR_ID

    if(not(OUTRA_ELEICAO_COM_MAIOR_ID)):
        print("Iniciando eleição! ")
        MINHA_ELEICAO = True
        enviar_mensagem(MSG_ELEICAO, broadcast = True)
        QTD_ENV_ELEICAO += 1
        time.sleep(16)
        if(MINHA_ELEICAO):
            print("Eu venci a eleição! ")
            enviar_mensagem(MSG_COORDENADOR, broadcast = True)
            QTD_ENV_COORDENADOR +=1
        else:
            print("Eu perdi a eleição <°(((><")
    else:
        print("Outra eleição com maior ID em andamento")


def sair_da_lista():
    print("Programa fechando")
    global MY_PORT
    global DEVO_MORRER
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

def imprimir_relatorio():

    global QTD_ENV_VIVO
    global QTD_ENV_VIVO_OK
    global QTD_ENV_ELEICAO
    global QTD_ENV_COORDENADOR
    global QTD_ENV_OK

    global QTD_REC_VIVO
    global QTD_REC_VIVO_OK
    global QTD_REC_ELEICAO
    global QTD_REC_COORDENADOR
    global QTD_REC_OK

    RELATORIO = f"\nEnviadas:\nELEIÇÂO:{QTD_ENV_ELEICAO}\nREI:{QTD_ENV_COORDENADOR}\nVIVO:{QTD_ENV_VIVO}\nVIVO_OK:{QTD_ENV_VIVO_OK}\nOK:{QTD_ENV_OK}\n\nRecebidas:\nELEIÇÂO:{QTD_REC_ELEICAO}\nREI:{QTD_REC_COORDENADOR}\nVIVO:{QTD_REC_VIVO}\nVIVO_OK:{QTD_REC_VIVO_OK}\nOK:{QTD_REC_OK}\n"

    print(RELATORIO)

def doença_do_rei():
    while True:
        if (KING_ID == MY_PORT):
            FINGINDO_MORTO = True
            return

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
    thread_que_verifica_king.join()

    message = input("Saindo.. Pressione enter para continuar... ")
