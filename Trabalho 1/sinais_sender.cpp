#include <sys/types.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>

using namespace std;


int main (int argc, char *argv[]) {
   
   if(argc<=1) {
        cout<<"You did not feed me arguments, I will die now :( ..."<<endl;
        exit(1);
   } 
   
   pid_t pidToSend = atoi(argv[1]);
   int sig = atoi(argv[2]);

   if (kill(pidToSend, 0)==0){ 

      cout<< "Enviando sinal " << sig << " para o processo " << pidToSend << endl;

      kill(pidToSend, sig);

   }

   else{

      cout<< "Erro - O processo " << pidToSend << " não existe" << endl;

   }

   return 0;
}
