public class Main {
    public static void main(String[] args) {
        Profesor p1 = new Profesor("Ana Torres", "Sistemas", 20);
        ProfesorTitular p2 = new ProfesorTitular("Dr. Carlos Vega", "Sistemas", 15, 8000, 12);
        
        Profesor[] profesores = {p1, p2};
        for (Profesor p : profesores) {
            System.out.println(p.getInfo());
        }
    }
}