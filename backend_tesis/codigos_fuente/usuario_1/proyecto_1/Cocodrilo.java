public class Cocodrilo extends Animal {

    // --- Atributos Propios ---
    private int mordida;

    // --- Constructores ---
    public Cocodrilo() {
        super(); // Llama al constructor del padre
    }

    public Cocodrilo(int age, String gender, int mordida) {
        super(age, gender); // Inicializa atributos del padre
        this.mordida = mordida;
    }

    // --- Métodos heredados de Animal (Ejemplo de sobreescritura) ---
    @Override
    public void isFamele() {
        // Puedes agregar lógica extra aquí
        super.isFamele(); // Llama a la versión del padre
    }

}