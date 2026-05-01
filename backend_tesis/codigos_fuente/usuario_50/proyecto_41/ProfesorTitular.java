public class ProfesorTitular extends Profesor {
    private double bonoInvestigacion;
    private int publicaciones;

    public ProfesorTitular(String nombre, String departamento, int horasClase, double bonoInvestigacion, int publicaciones) {
        super(nombre, departamento, horasClase);
        this.bonoInvestigacion = bonoInvestigacion;
        this.publicaciones = publicaciones;
    }

    public double calcularSalario() {
        return super.calcularSalario() + bonoInvestigacion + (publicaciones * 500);
    }

    public String getInfo() {
        return super.getInfo() + " | Publicaciones: " + publicaciones;
    }
}