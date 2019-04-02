package main

import (
    "log"
	"net"
	"strconv"
    "strings"
    "math/rand"
    "time"
    "flag"
)



const (
	StopCharacter = "\r\n\r\n"
)

func SocketClient(ip string, port int, N int) {

    rand.Seed(time.Now().UnixNano())
    min := 1
    max := 100
    number := rand.Intn(max - min) + min

    for i:=0;i<N;i++{

        delta   := rand.Intn(max - min) + min  
        number = number + delta

        if(i==N-1){
            number = -1
        }

        message:=strconv.Itoa(number)

        addr := strings.Join([]string{ip, strconv.Itoa(port)}, ":")
        conn, err := net.Dial("tcp", addr)

        defer conn.Close()

        if err != nil {
            log.Fatalln(err)
        }
        
        conn.Write([]byte(message))
        conn.Write([]byte(StopCharacter))
        

        buff := make([]byte, 1024)
        n, _ := conn.Read(buff)
        log.Printf("Enviou: %s - Recebeu %s", message,buff[:n])
        log.Printf("\n")
    }

}

func main() {

    // go run client_socket.go -n=200

	var (
		ip   = "127.0.0.1"
		port = 3333
    )

    log.Printf("Produtor iniciando ")

    N:= flag.Int("n", 100, "number of iterations")
    // Parse the flags.
    flag.Parse()

    SocketClient(ip, port, *N)
    
    log.Printf("Produtor saindo... ")

}