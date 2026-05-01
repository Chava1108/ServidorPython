public class Profesor {
    protected String nombre;
    protected String departamento;
    protected int horasClase;

    public Profesor(String nombre, String departamento, int horasClase) {
        this.nombre = nombre;
        this.departamento = departamento;
        this.horasClase = horasClase;
    }

    public double calcularSalario() {
        return horasClase * 250.0;
    }

    public String getInfo() {
        return "Profesor: " + nombre + " | Depto: " + departamento + " | Salario: $" + calcularSalario();
    }
}