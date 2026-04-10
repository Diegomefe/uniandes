from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from reportes.models import Facturacion_Consolidada
from recurso_cloud.monitoreo_mv import extraerGastosAWS, extraerGastosGCP

class Command(BaseCommand):

    def consolidarGastos(self, *args, **options):
        periodo_str = options.get('periodo') or datetime.now(timezone.utc).strftime("%Y-%m")
        periodo = datetime.strptime(periodo_str, "%Y-%m").replace(tzinfo=timezone.utc)
        self.stdout.write(f"Procesando datos para el periodo: {periodo_str}")

        inicio_mes = periodo.replace(day=1, hour=0, minute=0, second=0, microsecond=0)        

        cpu_mensual_aws, trafico_gb_aws, costo_estimado_aws = extraerGastosAWS(inicio_mes, periodo)
        cpu_gcp, trafico_gb_gcp, costo_gcp = extraerGastosGCP(inicio_mes, periodo)

        costo_total = costo_gcp + costo_estimado_aws

        
        Facturacion_Consolidada.objects.update_or_create(mes = periodo_str, defaults={'cpu_avg_aws': round(cpu_mensual_aws,2), 'costo_aws': round(costo_estimado_aws, 2), 'netOut_gb_aws': round(trafico_gb_aws,2), 'cpu_avg_gcp': round(cpu_gcp,2), 'costo_gcp': round(costo_gcp, 2), 'netOut_gb_gcp': round(trafico_gb_gcp,2), 'costo_total': costo_total})

        


