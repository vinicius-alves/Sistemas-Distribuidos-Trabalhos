#include <unistd.h>
#include <iostream>
#include <vector>
#include <thread> 
#include <cmath>
#include <chrono>
#include <atomic> 

#define VALOR_MAXIMO  100
#define VALOR_MINIMO -100
#define QTD_EXECUCOES 100000

using namespace std;
typedef char BYTE;
atomic_flag lock_stream = ATOMIC_FLAG_INIT;

// g++ somador.cpp -o somador -pthread 

vector<thread> threads;
uint k;
uint n;
bool lock; 
bool nano_sec;
int resultado_soma;
BYTE *array_para_somar;

void preencher_array(){

   srand(time(NULL));

   int distancia = VALOR_MAXIMO - VALOR_MINIMO;

   for(int i = 0; i<n;i++)
      array_para_somar[i] = ((rand()%distancia) +1)+VALOR_MINIMO;

}

bool test_and_set(){


   //bool anterior = lock;
 	//lock = true;
 	//return anterior;

 	bool result = lock_stream.test_and_set();
 	return result;

}

void acquire(){

	while(test_and_set());

}

void release(){

	//lock = false;
   lock_stream.clear();

}

void job_thread (int id){

   uint parcela = floor(n/k);

   uint limite_inicial = parcela*id;
   uint limite_final   = parcela*(id+1);

   if(id == k-1)
      limite_final = n;

   int acumulador_local = 0;

   for (uint i =limite_inicial; i<limite_final; i++)
      acumulador_local += array_para_somar[i];

   acquire();

   resultado_soma += acumulador_local;

   release();
}


int computar_soma(){

   lock = false; 
   resultado_soma = 0;

   auto start = chrono::steady_clock::now();

   preencher_array();

   threads.clear();

   for (int i =0; i<k;i++) 
      threads.push_back(thread(job_thread,i));
  

   for (auto& th : threads) 
      th.join();

   auto end = chrono::steady_clock::now();

   auto diff = end - start;

   int time_ms;

   if(nano_sec)
      time_ms = chrono::duration <double, nano> (diff).count();
   else
      time_ms = chrono::duration <double, milli> (diff).count();
   
   return time_ms;

}

double media ( vector<int>& v ) {

   double valor_retorno = 0.0;
   int n = v.size();
       
   for ( int i=0; i < n; i++)
      valor_retorno += v[i];
         
   return ( valor_retorno / n);
}


int main (int argc, char *argv[]) {
   
   if(argc<=1){ 

      k = 4;
      n = 200;

   }  else {

      k = atoi(argv[1]);
      n = atoi(argv[2]);
   }

   if(n<1000)
      nano_sec = true;
   else
      nano_sec = false;   

   array_para_somar = new BYTE[n];

   int tempo_exec;
   vector<int> tempo_exec_vec(QTD_EXECUCOES);

   for(uint i =0; i<QTD_EXECUCOES;i++){
      tempo_exec = computar_soma();
      tempo_exec_vec[i] = tempo_exec;
   }
      
   cout<< "Tempo de execução médio: "<<media(tempo_exec_vec);

   if(nano_sec)
      cout<<" ns." <<endl;
   else
      cout<<" ms." <<endl;
   
   return 0;
}
