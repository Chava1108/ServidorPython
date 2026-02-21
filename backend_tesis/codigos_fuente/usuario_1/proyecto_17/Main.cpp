#include <iostream>
using namespace std;

int main() {
// 1. Creación de objeto en el "Stack" (Memoria automática, lo más común en ejercicios)
    Perro miPerro("Hachi");
    
    // 2. Llamada a métodos
    miPerro.hacerSonido();

    // 3. Probando el polimorfismo
    Animal* animalGenerico = &miPerro;
    animalGenerico->hacerSonido(); // Llamará al de Perro por el 'virtual'

    return 0; // C++ requiere retornar un entero
}