public class Zebra extends Animal {

    // --- Atributos Propios ---
    private boolean is_wild;

    // --- Constructores ---
    public Zebra() {
        super(); // Llama al constructor del padre
    }

    public Zebra(int age, String gender, boolean is_wild) {
        super(age, gender); // Inicializa atributos del padre
        this.is_wild = is_wild;
    }

    // --- Métodos Propios ---
    public void run() {
    }

    // --- Métodos heredados de Animal (Ejemplo de sobreescritura) ---
    @Override
    public void isFamele() {
        // Puedes agregar lógica extra aquí
        super.isFamele(); // Llama a la versión del padre
    }

}