public class Duck extends Animal {

    // --- Atributos Propios ---
    private int sizeInFeet;

    // --- Constructores ---
    public Duck() {
        super(); // Llama al constructor del padre
    }

    public Duck(int age, String gender, int sizeInFeet) {
        super(age, gender); // Inicializa atributos del padre
        this.sizeInFeet = sizeInFeet;
    }

    // --- Métodos Propios ---
    public void swim() {
    }

    public int quack() {
        return 0;
    }

    // --- Métodos heredados de Animal (Ejemplo de sobreescritura) ---
    @Override
    public void isFamele() {
        // Puedes agregar lógica extra aquí
        super.isFamele(); // Llama a la versión del padre
    }

}