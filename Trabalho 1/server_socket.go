package main

import (
    "bufio"
	"log"
	"net"
	"os"
	"strconv"
    "strings"
    "math"
)

const (
	StopCharacter = "\r\n\r\n"
)

func SocketServer(port int) {

	listen, err := net.Listen("tcp4", ":"+strconv.Itoa(port))
	defer listen.Close()
	if err != nil {
		log.Fatalf("Socket listen port %d failed,%s", port, err)
		os.Exit(1)
	}
	log.Printf("Begin listen port: %d", port)

	for {
		conn, err := listen.Accept()
		if err != nil {
			log.Fatalln(err)
			continue
		} 
        handler(conn)
	}

}

func handler(conn net.Conn) {

	defer conn.Close()

	var (
		buf = make([]byte, 1024)
		r   = bufio.NewReader(conn)
		w   = bufio.NewWriter(conn)
    )
    
    var data string

    n, err := r.Read(buf)
    data = string(buf[:n])

    switch err {

        case nil:
            if isTransportOver(data) {
                
            }

        default:
            log.Fatalf("Receive data failed:%s", err)
            return
    }
        
    
    i, err_ := strconv.ParseInt(data,10, 32)
    if(err_!= nil){}
    result := isPrime(int(i))

	w.Write([]byte(result))
	w.Flush()
    log.Printf("Recebido: %s - Enviado: %s", data, result)
    log.Printf("\n")

}

func isPrime(value int) string {
    for i := 2; i <= int(math.Floor(float64(value) / 2)); i++ {
        if value%i == 0 {
            return "false"
        }
    }

    if(value > 1){
        return "true"
    } else{
        return "false"
    }

}

func isTransportOver(data string) (over bool) {
	over = strings.HasSuffix(data, "\r\n\r\n")
	return
}

func main() {

    // go run server_socket.go

	port := 3333

	SocketServer(port)

}