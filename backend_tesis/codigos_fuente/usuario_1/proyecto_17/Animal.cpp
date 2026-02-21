#include <iostream>
#include <string>
using namespace std;

class Animal {
public:
    string nombre;
// --- Constructores ---
    Animal() {}
    Animal(String nombre) : nombre(nombre) {}

    // --- Métodos Propios ---
    virtual void hacerSonido() {
        cout << nombre << " hace un sonido genérico." << endl;
    }

};