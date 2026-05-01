public class Main {
    public static void main(String[] args) {
        ArticuloCientifico a1 = new ArticuloCientifico("IA en Educacion", "Dr. Lopez");
        ArticuloCientifico a2 = new ArticuloCientifico("Redes Neuronales", "Dra. Garcia", 2023);
        ArticuloCientifico a3 = new ArticuloCientifico("Deep Learning", "Dr. Martinez", 2022, "IEEE", "10.1109/xyz");
        System.out.println(a1.getCita());
        System.out.println(a2.getCita());
        System.out.println(a3.getInfo());
    }
}