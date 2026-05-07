from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Facturacion_Consolidada
from recurso_cloud.management.commands.actualizar_costos import Command as Recolectar
from django.forms.models import model_to_dict


def health_check(request):
    return HttpResponse("OK", status=200)

def reporteGastos(request):
    
    empresa = request.GET.get('empresa', 'Beta Corp')
    periodo = request.GET.get('periodo', '2026-01')
    reporte = Facturacion_Consolidada.objects.filter(mes=periodo, empresa=empresa).first()

    valido, mensaje = reporte.verificar_integridad()
    if not valido:
        return JsonResponse({'status': 'error', 'mensaje': mensaje}, status = 403)

    if not reporte:
        Recolectar().consolidarGastos(periodo = periodo)
        reporte = Facturacion_Consolidada.objects.filter(mes=periodo, empresa=empresa).values().first()
    reporte = model_to_dict(reporte)
    return JsonResponse(reporte)

