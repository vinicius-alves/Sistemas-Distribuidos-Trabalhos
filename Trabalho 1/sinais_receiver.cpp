#include <iostream>
#include <csignal>
#include <thread>
#include <chrono>
#include <sys/types.h>
#include <unistd.h>
#include <mutex>
#include <condition_variable>

using namespace std;

mutex mtx;
condition_variable cv;

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

bool acordar() {return false;}

int main (int argc, char *argv[]) {
  
   signal(SIGINT , signalHandler); // 2
   signal(SIGQUIT, signalHandler); // 3 
   signal(SIGILL , signalHandler); // 4
   signal(SIGTRAP, signalHandler); // 5

   
   cout << "Processo " << getpid() <<endl;

   int seletorModo =  atoi(argv[1]);

   if(seletorModo == 1){

      cout<<"Busy Wait"<<endl;
      while(1) { }

   }

   else {

      cout<<"Blocking Wait"<<endl;
      unique_lock<mutex> lck(mtx);
      cv.wait(lck,acordar);

   }
   

   return 0;
}
