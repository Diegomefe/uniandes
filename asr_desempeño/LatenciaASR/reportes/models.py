from django.db import models

class Facturacion_Consolidada(models.Model):
    mes = models.CharField(max_length=7, unique=True) # 2026-04
    cpu_avg_aws = models.FloatField(default=0.0)
    netOut_gb_aws = models.FloatField(default=0.0)
    cpu_avg_gcp = models.FloatField(default=0.0)  
    netOut_gb_gcp = models.FloatField(default=0.0)  
    costo_aws = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    costo_gcp = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def guardar(self, *args, **kwargs):
        self.costo_total = float(self.costo_aws) + float(self.costo_gcp)
        super(Facturacion_Consolidada, self).save(*args, **kwargs)

    def __str__(self):
        return f"Reporte de {self.mes} - Total: ${self.costo_total}"
