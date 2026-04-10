from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Facturacion_Consolidada
from recurso_cloud.management.commands.actualizar_costos import Command as Recolectar

def health_check(request):
    return HttpResponse("OK", status=200)

def reporteGastos(request):
    
    empresa = request.GET.get('empresa', 'Generica')
    periodo = request.GET.get('periodo', '2026-04')
    reporte = Facturacion_Consolidada.objects.filter(mes=periodo, empresa=empresa).values().first()

    if not reporte:
        Recolectar().consolidarGastos(periodo = periodo)
        reporte = Facturacion_Consolidada.objects.filter(mes=periodo, empresa=empresa).values().first()
    
    return JsonResponse(reporte)

