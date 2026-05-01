public class Main {
    public static void main(String[] args) {
        Pedido p = new Pedido("Laptop", 2, 15000.0);
        System.out.println(p.mostrarResumen());
        System.out.println("Con descuento: $" + p.calcularTotal(10));
        System.out.println("Con descuento y envio: $" + p.calcularTotal(10, 250));
    }
}