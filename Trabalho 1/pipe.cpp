
#include <unistd.h>
#include <iostream>


using namespace std;

int pipefd[2];
pid_t cpid;


bool e_primo(int n){

   if(n == 2) 
   return true;

   for(int i = 2; i < n; i++){

      if(n%i == 0) 
         return false;
   }

   return true;
}


void processo_consumidor(){

   close(pipefd[1]);

   int number;
   
   while(read(pipefd[0], &number, sizeof(number)) > 0){

      if(e_primo(number))
         cout<<"Número "<<number<<" é primo."<<endl;

      else
         cout<<"Número "<<number<<" não é primo."<<endl;
 
   }

   cout<< "Consumidor saindo ..."<<endl;

}

void processo_produtor(int qtd_numeros = 1000){


   close(pipefd[0]);

   int number=1;

   srand(time(NULL));

   for(int i = 0; i<qtd_numeros; i++) {

      if(i+1 == qtd_numeros) {

         cout << "Escrevendo número "<< number <<endl;
         write(pipefd[1], 0, sizeof(int));
      
      } else {

         number += rand()%100;
         cout << "Escrevendo número "<< number <<endl;
         write(pipefd[1], &number, sizeof(int));

      }

   }

   cout<< "Produtor saindo ..."<<endl;

}


int main (int argc, char *argv[]) {
   
   int qtd_numeros;

   if(argc<=1) 
      qtd_numeros = 1000;
   else
      qtd_numeros = atoi(argv[1]);
   

   if (pipe(pipefd) == -1) {
      cout<<"Erro - Não foi possível criar o pipe. "<<endl;
      exit(1);
   }
   
   cpid = fork();
   
   switch (cpid) {

      case -1:
         cout<<"Erro - Não foi possível criar o processo filho. "<<endl;
         exit(1);
         break;

      case 0:
         processo_consumidor();
         break;

      default:
         processo_produtor(qtd_numeros);
         break;

   }
   
   return 0;
}
