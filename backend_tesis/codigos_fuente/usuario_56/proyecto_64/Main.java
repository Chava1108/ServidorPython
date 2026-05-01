public class Main {
    public static void main(String[] args) {
        CuentaAhorros ahorro = new CuentaAhorros("Juan Perez", 10000, "AH-001", 5.0);
        CuentaCorriente corriente = new CuentaCorriente("Maria Lopez", 5000, "CC-001", 3000);
        
        ahorro.depositar(2000);
        ahorro.aplicarInteres();
        System.out.println(ahorro.getInfo());
        
        corriente.retirar(7000);
        System.out.println(corriente.getInfo());
    }
}