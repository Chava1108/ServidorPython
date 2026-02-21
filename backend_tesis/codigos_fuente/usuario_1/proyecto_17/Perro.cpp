#include <iostream>
#include <string>
using namespace std;

class Perro : public Animal {
public:
    int test;
// --- Constructores ---
    Perro() : Animal() {}
    Perro(string nombre, int test) : Animal(nombre), test(test) {}

    // --- Sobreescritura de Animal ---
    void hacerSonido() override {
        // Lógica de sobreescritura
        Animal::hacerSonido();
    }

};