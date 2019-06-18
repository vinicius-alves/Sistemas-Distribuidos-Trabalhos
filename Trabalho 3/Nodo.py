import socket
import time
import threading

                        #########SETUP INICIAL###########

# Cria o socket. AF_INET é IPv4.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# O "0"  no luga da porta faz com que o OS escolha uma porta livre por conta própria.
s.bind(("127.0.0.1", 0))

#Retorna uma tupla IP, porta, o índice [1] pega só a porta.
MY_PORT = s.getsockname()[1]
print("Estou na porta " + str(MY_PORT))
f = open("port_list.txt", "a")
f.write(str(MY_PORT) + "\n")
f.close()        

#Após escrever no arquivo, abre e lê para verificar se a primeira linha escrita é sua própria porta.
f = open("port_list.txt", "r")
ports_list = list(f)
#print("Presentes portas são: " + f.read())
f.close()

# Arquivo relatório
ARQUIVO_RELATORIO_CSV = "relatorio.csv"

# É setada em True para avisar todas as threads que devem iniciar harakiri.
DEVO_MORRER = False
# É setada true para que todas as threads parem de responder a mensagens
FINGINDO_MORTO = False

# Identificação do rei
KING_ID = int(ports_list[0])
KING_CHECKED = False
WAITING_KING = False
KING_SEMAPHORE = threading.BoundedSemaphore(1)
KING_SEMAPHORE.acquire(False)
print("O rei é", KING_ID,'\n')

# Semáforo para impressão
PRINT_SEMAPHORE = threading.BoundedSemaphore(1)
LAST_THREAD_TO_PRINT = - 1
PAUSE_PRINT = False


#Eventos que coordenarão a thread que verifica o rei e a thread da doença_do_rei.
IAM_KING = threading.Event() #Se True, thread que verifica o rei dorme.
IAM_NOT_KING = threading.Event()
#Se processo começar como rei, dou set() em IAM_KING
IAM_KING.set()
    

# Eleição
# Minha eleição está ocorrendo ou outra eleição de um nó com maior ID está ocorrendo.
MINHA_ELEICAO = False
OUTRA_ELEICAO_COM_MAIOR_ID = False
JA_TENTEI_ME_ELEGER = False
ELEICAO_SEMAPHORE = threading.BoundedSemaphore(1)
FINGINDO_MORTO_SEMAPHORE = threading.BoundedSemaphore(1)
FINGINDO_MORTO_SEMAPHORE.acquire(False)

#Definição das mensagens que serão recebidas pela thread que escuta mensagens.
MSG_VIVO    = "VIVO"
MSG_VIVO_OK = "VIVO_OK"
MSG_CLOSE   = "CLOSE"
MSG_ELEICAO = "ELEICAO"
MSG_OK      = "OK"
MSG_COORDENADOR = "COORDENADOR"
MSG_LIDER = str(s.getsockname()[1])

#Armazenamento do número de mensagens enviadas e recebidas de  cada tipo.
QTD_ENV_VIVO    = 0
QTD_ENV_VIVO_OK = 0
QTD_ENV_ELEICAO = 0
QTD_ENV_LIDER   = 0
QTD_ENV_OK      = 0

QTD_REC_VIVO    = 0
QTD_REC_VIVO_OK = 0
QTD_REC_ELEICAO = 0
QTD_REC_LIDER   = 0
QTD_REC_OK      = 0

#Relatório é impresso no terminal quando usuário emite o comando dados
RELATORIO = f"\nEnviadas:\nELEIÇÂO:{QTD_ENV_ELEICAO}\nREI:{QTD_ENV_LIDER}\nVIVO:{QTD_ENV_VIVO}\nVIVO_OK:{QTD_ENV_VIVO_OK}\n\nRecebidas:\nELEIÇÂO:{QTD_REC_ELEICAO}\nREI:{QTD_REC_LIDER}\nVIVO:{QTD_REC_VIVO}\nVIVO_OK:{QTD_REC_VIVO_OK}\n"

#Setup inicial do Nodo terminado, temos uma porta e ela está anotada no arquivo de referência: ports_list.txt

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
    global QTD_ENV_ELEICAO
    #global IAM_NOT_KING
    global FINGINDO_MORTO_SEMAPHORE

    #if (MY_PORT != KING_ID):
    #    IAM_NOT_KING.set()

    while not(DEVO_MORRER):
        #Espera até que não seja rei para verificar o rei.
        #IAM_NOT_KING.wait()
        KING_CHECKED = False
        WAITING_KING = True
        print_s(id_thread =3, string_to_print = "Tentando verificar o rei")
        #print("Tentando verificar o rei\n")
        QTD_ENV_VIVO += 1
        enviar_mensagem(MSG_VIVO, node_port = KING_ID, id_thread = 3)

        if(FINGINDO_MORTO):
            FINGINDO_MORTO_SEMAPHORE.acquire(True)
            continue

        time.sleep(8)

        if(not(KING_CHECKED) and not(FINGINDO_MORTO)):
            print_s(id_thread =3, string_to_print = "The king is dead!!\nAnarchy!\n ")
            iniciar_eleicao(id_thread = 3)
            KING_SEMAPHORE.acquire(True)


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
    global MSG_LIDER
    global MSG_OK
    global MSG_VIVO
    global MSG_VIVO_OK

    global QTD_REC_VIVO
    global QTD_REC_LIDER
    global QTD_REC_VIVO_OK
    global QTD_REC_ELEICAO
    global QTD_ENV_OK
    global QTD_ENV_VIVO_OK

    #global IAM_NOT_KING
    global IAM_KING
    global not_ultimo
    global PAUSE_PRINT

    global MY_PORT

    while (not DEVO_MORRER):        
        #buffer size is 1024 bytes. "data" is the message received, "addr" is the address of the sending process, which is a tuple (ip, port).
        try: 
            data, addr = s.recvfrom(1024)
            addr_port = addr[1]
            message = data.decode("utf-8") 

            m="Mensagem recebida: " + message + " de "+ str(addr_port)
            print_s(id_thread =1, string_to_print = m)

            if(message == MSG_VIVO):
                QTD_REC_VIVO += 1
                if (not(FINGINDO_MORTO)):
                    QTD_ENV_VIVO_OK += 1
                enviar_mensagem(MSG_VIVO_OK, node_port = addr_port, id_thread =1)

            if(message == MSG_OK):
                QTD_REC_VIVO_OK += 1
                MINHA_ELEICAO = False
            
            elif(message == MSG_VIVO_OK and addr_port == KING_ID and WAITING_KING):
                KING_CHECKED = True
                WAITING_KING = False

            elif(message == MSG_CLOSE):
                DEVO_MORRER = True
                sair_da_lista()
                break

            if(message == MSG_ELEICAO):
                QTD_REC_ELEICAO += 1
                if (MY_PORT > addr_port):
                    QTD_ENV_OK += 1
                    enviar_mensagem(MSG_OK, node_port = addr_port, id_thread =1)
                    iniciar_eleicao(id_thread =1)
                else:
                    OUTRA_ELEICAO_COM_MAIOR_ID = True

            if(message == MSG_COORDENADOR):
                QTD_REC_LIDER += 1
                JA_TENTEI_ME_ELEGER = False
                OUTRA_ELEICAO_COM_MAIOR_ID = False
                WAITING_KING = False
                KING_ID = addr_port
                KING_SEMAPHORE.release()
                #if (MY_PORT != KING_ID):
                #    IAM_NOT_KING.set()


            elif (message == "pause"):
                PAUSE_PRINT = True

            elif (message == "cotinue"):
                PAUSE_PRINT = False

            elif (message == "relatorio"):
                imprimir_relatorio_em_csv()

            #IFs daqui pra baixo são para implementação das funções que facilitaram a tomada de dados para o problema.
            elif (message == "doença"):
                thread_da_doença_do_rei.start()
            elif (message == "ultimo" and FINGINDO_MORTO == False):
                enviar_mensagem("ultimo_ok", node_port = addr_port, id_thread =1)
            elif (message == "ultimo_ok"):
                not_ultimo.set()


        except:
            pass
    print_s(id_thread =1, string_to_print = "Thread de escuta saindo")

'''
Comandos da Interface:

Close => encerra o processo do nó.
Terminar => encerra todos os nós.
Falhar => falha o nó, que para de responder mensagens dos outros nós.
Recuperar => faz o no voltar a responder mensagens.
Dados => imprime um relatório com todos os dados.
Doença => Libera a doença do rei: Assim que um nodo se torna rei, ele falha.
Rei => Informa quem é o rei atual. Se não ouver rei atual, informa que uma eleição está em andamento.
'''

def thread_interface():

    global DEVO_MORRER
    global MSG_CLOSE
    global RELATORIO
    global PAUSE_PRINT
    global FINGINDO_MORTO
    global FINGINDO_MORTO_SEMAPHORE
    
    while not(DEVO_MORRER):

        message = input("O que devo fazer agora? ")
        message = message.replace(' ','')
        message = message.lower()

        if (message == "close"):
            message = message.replace("close", MSG_CLOSE)
            enviar_mensagem(message, node_port = MY_PORT, id_thread =2)
            sair_da_lista()
        
        elif (message == "terminar"): 
            message = message.replace("terminar", MSG_CLOSE)
            enviar_mensagem(message, broadcast = True, id_thread =2)

        elif (message == "rei"):
            get_king()

        elif (message == "pause"):
            enviar_mensagem(message, broadcast = True, id_thread =2)

        elif (message == "cotinue"):
            enviar_mensagem(message, broadcast = True, id_thread =2)

        elif (message == "relatorio"):
            enviar_mensagem(message, broadcast = True, id_thread =2)
            
        elif (message == "falhar"):
            FINGINDO_MORTO = True

        elif (message == "recuperar"):
            FINGINDO_MORTO = False
            FINGINDO_MORTO_SEMAPHORE.release()

        elif (message == "dados"):
            imprimir_relatorio(id_thread = 2)

        elif (message == "doença"):
            enviar_mensagem(message, broadcast = True, id_thread =2)
        time.sleep(0.2)

    print_s(id_thread =2, string_to_print = "Thread de interface saindo...")

    
#Definição das funções que serão chamadas dentro das threads
    
def get_king():
    if (not WAITING_KING):
        m="O atual rei é: " + str(KING_ID) + "\n"+"Longa vida ao rei!"
    else:
        m="Nosso rei foi decapitado, estamos escolhendo outro.\n" + "Não fui eu que decapitei ok?"

    print_s(id_thread =2, string_to_print = m)

def enviar_mensagem(message, node_port=-1, broadcast = False, id_thread = -1, print_message = True): 

    global FINGINDO_MORTO
    if(FINGINDO_MORTO):
        return 0

    try:

        if(broadcast):
            counter = 0
            #opens the ports file with the "r" option, read_only.
            f = open("port_list.txt", "r")
            ports = list(f)
            #iterates over every line in the file. For python each line works as an element in an array.
            for node in ports:
                counter += 1
                s.sendto(message.encode("utf-8"), ("127.0.0.1", int(node)))
            f.close()

            m = "Mensagem enviada: " + str(message) + " para todos os nós"
            if(print_message):
                print_s(id_thread = id_thread, string_to_print = m)
            return counter
        else:
            s.sendto(message.encode("utf-8"), ("127.0.0.1", int(node_port)))
            m = "Mensagem enviada: " + str(message) + " para "+ str(node_port) 
            if(print_message):
                print_s(id_thread = id_thread, string_to_print = m)
            return 1
    except:
        if(broadcast):
            m = "Ocorreu um erro ao enviar " + message+" em broadcast"
        else:
            m = "Ocorreu um erro ao enviar " + message+" para o nó "+str(node_port)

        if(print_message):    
            print_s(id_thread = id_thread, string_to_print = m)

        return 0



#Funções que serão chamadas pela thread que verifica o rei.
def iniciar_eleicao(id_thread):

    global ELEICAO_SEMAPHORE
    global MINHA_ELEICAO
    global OUTRA_ELEICAO_COM_MAIOR_ID
    global KING_SEMAPHORE
    global JA_TENTEI_ME_ELEGER
    global QTD_ENV_LIDER 
    global QTD_ENV_ELEICAO

    ELEICAO_SEMAPHORE.acquire(True)

    if(not(JA_TENTEI_ME_ELEGER) and not(OUTRA_ELEICAO_COM_MAIOR_ID)):
        JA_TENTEI_ME_ELEGER = True
        MINHA_ELEICAO = True
        ELEICAO_SEMAPHORE.release()

        print_s(id_thread = id_thread, string_to_print = "Iniciando eleição! ")
        qtd_nodes = enviar_mensagem(MSG_ELEICAO, broadcast = True, id_thread = id_thread)
        QTD_ENV_ELEICAO +=qtd_nodes
        time.sleep(16)
        if(MINHA_ELEICAO):
            m = "Eu venci a eleição! "
            IAM_KING.set()
            qtd_nodes = enviar_mensagem(MSG_COORDENADOR, broadcast = True, id_thread = id_thread)
            QTD_ENV_LIDER +=qtd_nodes
        else:
            m = "Eu perdi a eleição <°(((><"
        print_s(id_thread = id_thread, string_to_print = m)
    else:    
        ELEICAO_SEMAPHORE.release()
    


def sair_da_lista():
    print("Programa fechando")
    global MY_PORT
    global DEVO_MORRER
    #guarda as linhas do arquivo na variável f
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

def print_s(id_thread, string_to_print):

    global PAUSE_PRINT
    if(PAUSE_PRINT):
        return

    global PRINT_SEMAPHORE
    global LAST_THREAD_TO_PRINT
    PRINT_SEMAPHORE.acquire(True)

    if(LAST_THREAD_TO_PRINT != id_thread):
        print("#########################################################\n")

        if(id_thread) == 1:
            print("Thread que escuta mensagens:  \n")
        elif(id_thread) == 2:
            print("Thread interface:  \n")
        elif(id_thread) == 4:
            print("Thread último:  \n")  
        elif(id_thread) == 5:
            print("Thread doença do rei:  \n")      
        else: 
            print("Thread que verifica o rei: \n")

    print(string_to_print)

    print("\n")

    LAST_THREAD_TO_PRINT = id_thread

    #print("O que devo fazer agora? \n")

    PRINT_SEMAPHORE.release()


def imprimir_relatorio(id_thread):

    global QTD_ENV_VIVO
    global QTD_ENV_VIVO_OK
    global QTD_ENV_ELEICAO
    global QTD_ENV_LIDER
    global QTD_ENV_OK

    global QTD_REC_VIVO
    global QTD_REC_VIVO_OK
    global QTD_REC_ELEICAO
    global QTD_REC_LIDER
    global QTD_REC_OK

    #fString com relatório formatado.
    RELATORIO = f"\nEnviadas:\nELEIÇÂO:{QTD_ENV_ELEICAO}\nREI:{QTD_ENV_LIDER}\nVIVO:{QTD_ENV_VIVO}\nVIVO_OK:{QTD_ENV_VIVO_OK}\nOK:{QTD_ENV_OK}\n\nRecebidas:\nELEIÇÂO:{QTD_REC_ELEICAO}\nREI:{QTD_REC_LIDER}\nVIVO:{QTD_REC_VIVO}\nVIVO_OK:{QTD_REC_VIVO_OK}\nOK:{QTD_REC_OK}\n"

    print_s(id_thread = id_thread, string_to_print = RELATORIO)

def imprimir_relatorio_em_csv():

    global QTD_ENV_VIVO
    global QTD_ENV_VIVO_OK
    global QTD_ENV_ELEICAO
    global QTD_ENV_LIDER
    global QTD_ENV_OK

    global QTD_REC_VIVO
    global QTD_REC_VIVO_OK
    global QTD_REC_ELEICAO
    global QTD_REC_LIDER
    global QTD_REC_OK

    global ARQUIVO_RELATORIO_CSV
    global MY_PORT

    
    #header = "IDPROCESSO; QTD_ENV_ELEICAO; QTD_ENV_LIDER; QTD_ENV_VIVO; QTD_ENV_VIVO_OK; QTD_REC_ELEICAO; QTD_REC_LIDER; QTD_REC_VIVO; QTD_REC_OK; QTD_REC_VIVO_OK"
    linha = str(MY_PORT) + '; '+ str(QTD_ENV_ELEICAO)+ '; '+ str(QTD_ENV_LIDER)+ '; '+ str(QTD_ENV_VIVO)+ '; '+ str(QTD_ENV_VIVO_OK)+ '; '+ str(QTD_REC_ELEICAO)+ '; '+\
    str(QTD_REC_LIDER)+ '; '+str(QTD_REC_VIVO)+ '; '+str(QTD_REC_OK)+ '; '+str(QTD_REC_VIVO_OK)

    f = open(ARQUIVO_RELATORIO_CSV, "a")
    f.write(linha + "\n")
    f.close() 


#Função executada pela thread da doença do rei. Assim que o processo vira rei ele falha.
def doença_do_rei():
    global FINGINDO_MORTO
    print_s(id_thread =5, string_to_print = "Ó não, fui afligido por uma doença perniciosa!")
    IAM_KING.wait()    
    FINGINDO_MORTO = True

#Definição de função que vai servir para impressão do relatório de avaliação no final do programa.
not_ultimo = threading.Event()
not_ultimo.set()
def thread_ultimo():
    global not_ultimo
    while (not_ultimo.is_set()):
        not_ultimo.clear()
        enviar_mensagem("ultimo", broadcast=True, id_thread = 4)
        try:
            not_ultimo.wait(timeout=3)           
        except:
            imprimir_relatorio(id_thread=4)
            enviar_mensagem(MSG_CLOSE, broadcast=True, id_thread = 4)
        time.sleep(8)


# CHAMANDO THREADS
if __name__ == "__main__":

    ################Criando as threads################

    # Thread responsável por receber mensagens e tomar ações.
    thread_escuta_mensangens = threading.Thread(target=thread_escuta_mensangens, args=())

    # Thread responsável por gerenciar interface com usuário
    thread_interface = threading.Thread(target=thread_interface, args=())

    # Thread responsável em detectar a presença do líder
    thread_que_verifica_king = threading.Thread(target=thread_que_verifica_king, args=())

    thread_ultimo = threading.Thread(target=thread_ultimo, daemon = True)

    #Thread que espera o processo se tornar rei e falha esse processo.Tem que ser uma Daemon thread, isso faz com que o programa possa finalizar sem esperar essa thread terminar.
    thread_da_doença_do_rei = threading.Thread(target= doença_do_rei, daemon = True)


    ################Iniciando as threads################
    thread_interface.start()
    thread_escuta_mensangens.start()
    thread_que_verifica_king.start()
    #thread_ultimo.start()
    
    #Faz com que main espere as threads finalizarem antes de fechar.
    thread_interface.join()    
    thread_que_verifica_king.join()

    message = input("Saindo.. Pressione enter para continuar... ")
