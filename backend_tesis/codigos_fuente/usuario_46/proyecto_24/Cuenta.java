public class Cuenta {
    protected String titular;
    protected double saldo;
    protected String numeroCuenta;

    public Cuenta(String titular, double saldo, String numeroCuenta) {
        this.titular = titular;
        this.saldo = saldo;
        this.numeroCuenta = numeroCuenta;
    }

    public void depositar(double monto) {
        if (monto > 0) {
            saldo += monto;
        }
    }

    public boolean retirar(double monto) {
        if (monto > 0 && monto <= saldo) {
            saldo -= monto;
            return true;
        }
        return false;
    }

    public String getInfo() {
        return "Cuenta: " + numeroCuenta + " | Titular: " + titular + " | Saldo: $" + saldo;
    }

}