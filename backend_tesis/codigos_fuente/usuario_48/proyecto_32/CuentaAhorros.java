public class CuentaAhorros extends Cuenta {
    private double tasaInteres;

    public CuentaAhorros(String titular, double saldo, String numeroCuenta, double tasaInteres) {
        super(titular, saldo, numeroCuenta);
        this.tasaInteres = tasaInteres;
    }

    public void aplicarInteres() {
        double interes = saldo * tasaInteres / 100;
        saldo += interes;
    }

    public String getInfo() {
        return super.getInfo() + " | Tasa: " + tasaInteres + "%";
    }
}