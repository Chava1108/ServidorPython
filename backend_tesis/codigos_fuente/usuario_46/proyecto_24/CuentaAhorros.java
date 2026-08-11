public class CuentaAhorros extends Cuenta {
   private double tasaInteres;

   public CuentaAhorros(String var1, double var2, String var4, double var5) {
      super(var1, var2, var4);
      this.tasaInteres = var5;
   }

   public void aplicarInteres() {
      double var1 = this.saldo * this.tasaInteres / (double)100.0F;
      this.saldo += var1;
   }

   public String getInfo() {
      return super.getInfo() + " | Tasa: " + this.tasaInteres + "%";
   }
}