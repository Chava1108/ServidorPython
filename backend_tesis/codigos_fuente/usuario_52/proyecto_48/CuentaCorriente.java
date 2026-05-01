public class CuentaCorriente extends Cuenta {
    private double limiteCredito;

    public CuentaCorriente(String titular, double saldo, String numeroCuenta, double limiteCredito) {
        super(titular, saldo, numeroCuenta);
        this.limiteCredito = limiteCredito;
    }

    public boolean retirar(double monto) {
        if (monto > 0 && monto <= (saldo + limiteCredito)) {
            saldo -= monto;
            return true;
        }
        return false;
    }

    public String getInfo() {
        return super.getInfo() + " | Limite credito: $" + limiteCredito;
    }
}