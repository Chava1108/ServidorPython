public class Estudiante extends persona {

    // --- Atributos Propios ---
    private int grado;
    private char grupo;
    private String carreraTecnica;
    private float promedio;
    private float test2();

    // --- Constructores ---
    public Estudiante() {
        super(); // Llama al constructor del padre
    }

    public Estudiante(int edad, String nombre, char sexo, int grado, char grupo, String carreraTecnica, float promedio, float test2()) {
        super(edad, nombre, sexo); // Inicializa atributos del padre
        this.grado = grado;
        this.grupo = grupo;
        this.carreraTecnica = carreraTecnica;
        this.promedio = promedio;
        this.test2() = test2();
    }

    // --- Métodos Propios ---
    public void aplicarExamen() {
    }

    // --- Métodos heredados de persona (Ejemplo de sobreescritura) ---
    @Override
    public void entrarJornada() {
        // Puedes agregar lógica extra aquí
        super.entrarJornada(); // Llama a la versión del padre
    }

}