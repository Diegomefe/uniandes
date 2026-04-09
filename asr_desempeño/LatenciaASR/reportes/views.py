from django.shortcuts import render
from django.http import JsonResponse
from .models import Facturacion_Consolidada
from recurso_cloud.management.commands.actualizar_costos import Command as Recolectar

def reporteGastos(request):

    periodo = request.GET.get('periodo', '2026-04')
    reporte = Facturacion_Consolidada.objects.filter(mes=periodo).values().first()

    if not reporte:
        Recolectar().extraerGastos(periodo = periodo)
        reporte = Facturacion_Consolidada.objects.filter(mes=periodo).values().first()
    
    return JsonResponse(reporte)

