#include <sys/types.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>

using namespace std;


int main (int argc, char *argv[]) {
   // register signal SIGINT and signal handler 

   if(argc<=1) {
        cout<<"You did not feed me arguments, I will die now :( ..."<<endl;
        exit(1);
   } 
   
   pid_t pidToSend = atoi(argv[1]);
   int sig = atoi(argv[2]);

   //TODO: dar erro quando processo não existir
   cout<< "Sending signal " << sig << " to process " << pidToSend << endl;

   kill(pidToSend, sig);



   return 0;
}
