#include <iostream>
#include <pthread.h>
#include <thread>
#include <mutex>
#include <chrono>
#include <condition_variable>
#include <random>
#include <cstring>
#include <math.h>
#include <vector>
#include <algorithm>

std::mutex mtx_empty, mtx_full, mtx;
std::condition_variable cond_full, cond_mtx, cond_empty; // "cond" s the condtion_variable element that will be responsible for managing the semaphore "mtx"

//  g++ -std=c++11 -pthread main.cpp

//#############################  My globals  ##############################################

const int N = 1; //tamanho da memoria compartilhada.
int free_pos = N; //number of free array positions on the beginning.

int np = 1; //number of producer threads.
int nc = 1; //number of consumer threads.
int M = pow(10, 5); //quantidade de números a gerar/consumir.

int mem_compartilhada[N]; //define um array, que será usado como memória compartilhada.
int full = 0;
int empty = N;

//########################################################################################

int random_num() {

    std::random_device rd; // obtain a random number from hardware
    std::mt19937 eng(rd()); // seed the generator
    std::uniform_int_distribution<> distr(25, 63); // define the range

    return distr(eng); //return the number generated
}

int look_for_food() //finds a valid number in the array to be consumed
{
    for( int a = 0; a <= N; a++ )
    {
        if (mem_compartilhada[a] != 0 )
            return a;
    }

    return 0;
}

int look_for_space() // Looks for free space to hold value produced
{
    for( unsigned int a = 0; a < N; a++ )
    {
        if (mem_compartilhada[a] == 0)
            return a;
    }
    std::cout << "fiz a busca";
    return 0;
}


bool e_primo(int n) //tests primality
{

    if(n == 2)
        return true;

    for(int i = 2; i < n; i++){

        if(n%i == 0)
            return false;
    }

    return true;
}

void consumidor(int id) //my consumer thread code
{
    while (true) {
        std::cout << "consumer thread " << id << " entered the loop\n" ;
        //binds the var "lock" to the semaphore mtx.
        std::unique_lock<std::mutex> lock_full(mtx_full);
        std::unique_lock<std::mutex> lock_mtx(mtx);
        //waits until there is a free position.
        cond_full.wait(lock_full, []{return full != 0;});
        std::cout << "consumer thread " << id << " passed lock_full\n" ;
        cond_mtx.wait(lock_mtx);
        std::cout << "consumer thread " << id << " passed mtx\n" ;
        //Then loops through array looking for food...
        int food = look_for_food();
        //Checks this "food" primality...
        int result = e_primo(mem_compartilhada[food]);
        //Prints result to terminal...
        char primality[] = {"no value"};
        if (result == 0) {
           strcpy(primality, "odd");
        } else {
            strcpy(primality, "even");
        }

        std::cout << "thread " << id << " consumed " << mem_compartilhada[food] << " a " << primality << " number " <<'\n';
        //Finally changes the value in the array to zero
        mem_compartilhada[food] = 0;
        //increases the value of empty reduces the value of full
        empty++;
        full--;
        // And notifies one thread waiting on the  condition_variable "cond" that it can go.
        cond_mtx.notify_one();
        return;
    }

}

void produtor(int id) { //My producer thread code

    while (true) {
        std::cout << "producer thread " << id << " entered the loop\n" ;
        if (M <= 0){
            std::cout << "Producer " << id << " finished\n";
        }
        std::unique_lock<std::mutex> lock_empty(mtx_empty);
        std::unique_lock<std::mutex> lock_mtx(mtx);
        //waits until there is a free space
        cond_empty.wait(lock_empty, []{return empty != 0;});
        std::cout << "producer thread " << id << " passed lock_empty\n" ;
        //then wait for mtx green light
        cond_mtx.wait(lock_mtx);
        std::cout << "producer thread " << id << " passed mtx\n" ;
        //Then loops through the array looking for empty space
        int empty = look_for_space();
        //generates random number
        int rand_num = random_num();
        //store it in the empty space
        mem_compartilhada[empty] = rand_num;
        //reduces one from the number of variables left to produce
        M = M -1;
        //increase the number of full spaces,
        full++;
        empty--;
        std::cout << "full is" << full;
        //notifies threads waiting on mtx
        cond_mtx.notify_one();
        return;
    }

}

void do_join(std::thread& t)
{
    t.join();
}

int main(int argc, char *argv[]) {

    std::cout << "We are your slaves, we produce, we consume!\n";

    int i;
    std::vector<std::thread> producer_threads;
    std::vector<std::thread> consumer_threads;

    for (i = 0; i < np; i++) {
        producer_threads.push_back(std::thread(produtor, i));
        std::cout << "Started producer n'" << i << "\n";
    }

    for (i = 0; i < nc; i++) {
        consumer_threads.push_back(std::thread(consumidor, i));
        std::cout << "Started consumer n'" << i << "\n";
    }

    //joins threads
    std::for_each(producer_threads.begin(),producer_threads.end(),do_join);
    std::for_each(consumer_threads.begin(),consumer_threads.end(),do_join);

    std::cout << M <<" numbers were produced\n";
    std::cout << "We have finished the work, Master\n";


    return 0;
}
