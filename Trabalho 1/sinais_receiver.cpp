#include <iostream>
#include <csignal>
#include <thread>
#include <chrono>
#include <sys/types.h>
#include <unistd.h>

using namespace std;

void signalHandler( int signum ) {
   cout << "Interrupt signal (" << signum << ") received.\n";

   // cleanup and close up stuff here  
   // terminate program  

   exit(signum);  
}

int main () {
   // register signal SIGINT and signal handler  
   signal(SIGINT, signalHandler);  

   cout << "Processo " << getpid() <<endl;

   while(1) {
      cout << "Aguardando...." << endl;
      this_thread::sleep_for(chrono::milliseconds(1000));
   }

   return 0;
}
