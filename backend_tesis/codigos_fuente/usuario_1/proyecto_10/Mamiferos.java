public class Mamiferos extends Animales {

    // --- Atributos Propios ---
    public int mesesGestacion;

    // --- Constructores ---
    public Mamiferos() {
        super(); // Llama al constructor del padre
    }

    public Mamiferos(int edad, int mesesGestacion) {
        super(edad); // Inicializa atributos del padre
        this.mesesGestacion = mesesGestacion;
    }

    // --- Métodos heredados de Animales (Ejemplo de sobreescritura) ---
    @Override
    public void comer() {
        // Puedes agregar lógica extra aquí
        super.comer(); // Llama a la versión del padre
    }

}