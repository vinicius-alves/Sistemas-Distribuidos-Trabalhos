#include <iostream>
#include <csignal>
#include <thread>
#include <chrono>
#include <sys/types.h>
#include <unistd.h>

using namespace std;

void signalHandler( int signum ) {

   cout << "\nSinal " << signum << " recebido"<<endl;

   switch (signum) {

      case 2:
         cout<<"Saindo... "<<endl;
         exit(1);
         break;

      case 3:
         cout<<"Mensagem 1 "<<endl;
         break;

      case 4:
         cout<<"Mensagem 2 "<<endl;
         break;

      case 5:
         cout<<"Mensagem 3 "<<endl;
         break;

   }
   
   
}

int main () {
  
   signal(SIGINT , signalHandler); // 2
   signal(SIGQUIT, signalHandler); // 3 
   signal(SIGILL , signalHandler); // 4
   signal(SIGTRAP, signalHandler); // 5

   
   cout << "Processo " << getpid() <<endl;

   while(1) {
      cout << "Aguardando...." << endl;
      this_thread::sleep_for(chrono::milliseconds(4000));
   }

   return 0;
}
