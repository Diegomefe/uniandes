from django.db import models
import hashlib

class Facturacion_Consolidada(models.Model):
    mes = models.CharField(max_length=7) # 2026-04
    empresa = models.CharField(max_length=100, default='Beta Corp')
    cpu_avg_aws = models.FloatField(default=0.0)
    netout_gb_aws = models.FloatField(default=0.0)
    cpu_avg_gcp = models.FloatField(default=0.0)
    netout_gb_gcp = models.FloatField(default=0.0)
    costo_aws = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    costo_gcp = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    hash = models.CharField(max_length=100, editable=False  )

    class Meta:
        unique_together = ('empresa', 'mes')

    def generarHash(self):
        data = f"{self.empresa}|{self.costo_total:.2f}|{self.mes}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verificar_integridad(self):
        hash_calculado = self.generarHash()

        if self.hash == hash_calculado:
            return True, "OK"
        else:
            return False, f"ALTERACIÓN DETECTADA: El hash guardado era {self.hash}, y el nuevo dato es {hash_calculado}"
        
    def save(self, *args, **kwargs):
        self.costo_total = float(self.costo_aws) + float(self.costo_gcp)
        self.hash = self.generarHash()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reporte de {self.mes} - Total: ${self.costo_total}"
