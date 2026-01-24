public class Perro extends Animal {

    // --- Atributos Propios ---
    private boolean ladrar;

    // --- Constructores ---
    public Perro() {
        super(); // Llama al constructor del padre
    }

    public Perro(int age, String gender, boolean ladrar) {
        super(age, gender); // Inicializa atributos del padre
        this.ladrar = ladrar;
    }

    // --- Métodos Propios ---
    private void correrRapido() {


        System.out.println("Perro corriendo");    
    
    
    }

    // --- Métodos heredados de Animal (Ejemplo de sobreescritura) ---
    @Override
    public void isFamele() {
        // Puedes agregar lógica extra aquí
        super.isFamele(); // Llama a la versión del padre
    }

}