public class ArticuloCientifico {
    private String titulo;
    private String autor;
    private int anioPublicacion;
    private String revista;
    private String doi;

    public ArticuloCientifico(String titulo, String autor) {
        this.titulo = titulo;
        this.autor = autor;
        this.anioPublicacion = 2024;
        this.revista = "Sin asignar";
        this.doi = "";
    }

    public ArticuloCientifico(String titulo, String autor, int anio) {
        this.titulo = titulo;
        this.autor = autor;
        this.anioPublicacion = anio;
        this.revista = "Sin asignar";
        this.doi = "";
    }

    public ArticuloCientifico(String titulo, String autor, int anio, String revista, String doi) {
        this.titulo = titulo;
        this.autor = autor;
        this.anioPublicacion = anio;
        this.revista = revista;
        this.doi = doi;
    }

    public String getCita() {
        return autor + " (" + anioPublicacion + "). " + titulo + ". " + revista;
    }

    public String getInfo() {
        return "Titulo: " + titulo + "\nAutor: " + autor + "\nAnio: " + anioPublicacion;
    }
}