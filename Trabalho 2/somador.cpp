
#include <unistd.h>
#include <iostream>
#include <vector>
#include <thread> 
#include <cmath>


#define VALOR_MAXIMO  100
#define VALOR_MINIMO -100

using namespace std;

vector<thread> threads;
uint k;
uint n;


typedef char BYTE;
BYTE *array_para_somar;

void preencher_array(){

   srand(time(NULL));

   int distancia = VALOR_MAXIMO - VALOR_MINIMO;

   for(int i = 0; i<n;i++)
      array_para_somar[i] = ((rand()%distancia) +1)+VALOR_MINIMO;

}

void job_thread (int id){

   uint parcela = floor(n/k);

   uint limite_inicial = parcela*id;
   uint limite_final   = parcela*(id+1);

   if(id == k-1)
      limite_final = n;

   int acumulador = 0;

   for (uint i =limite_inicial; i<limite_final; i++)
      acumulador += array_para_somar[i];

   cout<<"resultado = "<<acumulador<<endl;

   

  


}


void computar_soma(){

   preencher_array();

   for (int i =0; i<k;i++) 
      threads.push_back(thread(job_thread,i));
  

   for (auto& th : threads) 
      th.join();



}


int main (int argc, char *argv[]) {
   
   
   if(argc<=1){ 

      k = 4;
      n = 200;

   }  else {

      k = atoi(argv[1]);
      n = atoi(argv[2]);
   }

   array_para_somar = new BYTE[n];
   
   computar_soma();
   
   
   return 0;
}
