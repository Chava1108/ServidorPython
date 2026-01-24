public class Husky extends Perro {

    // --- Atributos Propios ---
    private long tamanio;

    // --- Constructores ---
    public Husky() {
        super(); // Llama al constructor del padre
    }

    public Husky(int age, String gender, boolean ladrar, long tamanio) {
        super(age, gender, ladrar); // Inicializa atributos del padre
        this.tamanio = tamanio;
    }

    // --- Métodos Propios ---
    private void ladrarFeo2() {
   
    
    }

}