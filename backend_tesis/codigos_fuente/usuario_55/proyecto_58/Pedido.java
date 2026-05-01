public class Pedido {
    private String producto;
    private int cantidad;
    private double precioUnitario;
    private String destino;

    public Pedido(String producto, int cantidad, double precioUnitario) {
        this.producto = producto;
        this.cantidad = cantidad;
        this.precioUnitario = precioUnitario;
        this.destino = "Local";
    }

    public double calcularTotal() {
        return cantidad * precioUnitario;
    }

    public double calcularTotal(double descuento) {
        double subtotal = cantidad * precioUnitario;
        return subtotal - (subtotal * descuento / 100);
    }

    public double calcularTotal(double descuento, double envio) {
        double subtotal = cantidad * precioUnitario;
        return subtotal - (subtotal * descuento / 100) + envio;
    }

    public String mostrarResumen() {
        return "Pedido: " + producto + " x" + cantidad + " - Total: $" + calcularTotal();
    }
}