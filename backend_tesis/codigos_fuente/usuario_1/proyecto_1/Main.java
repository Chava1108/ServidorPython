import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Animal perro = new Animal();
        perro.isFamele();
        try (// Instancia tus clases aquí y prueba tus métodos
        Scanner entrada = new Scanner(System.in)) {
            int edad = entrada.nextInt();
            int edad2 = entrada.nextInt();

            System.out.println("Hola Mundo la  edad sumada es: "+ (edad+ edad2));
            System.exit(0);
        }
    }
}