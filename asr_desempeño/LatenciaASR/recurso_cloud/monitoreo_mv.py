import os
import time
import boto3
from google.cloud import monitoring_v3
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta, timezone

def extraerGastosGCP(inicio, fin):
    duracion = int((fin - inicio).total_seconds())
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ubuntu/uniandes/asr_desempeño/LatenciaASR/gcp_key.json" #MODIFICAR
    client = monitoring_v3.MetricServiceClient()
    project_name = "projects/asrdesempeno"

    inicio_timestamp = Timestamp()
    inicio_timestamp.FromDatetime(inicio)
    fin_timestamp = Timestamp()
    fin_timestamp.FromDatetime(fin)

    interval = monitoring_v3.TimeInterval({
        "start_time": inicio_timestamp,
        "end_time": fin_timestamp,        
    })
    
    filtroCPU = (
        'metric.type = "compute.googleapis.com/instance/cpu/utilization" AND '
        'resource.labels.instance_id = "6309067129928439569"'
    )

    filtroNet = (
        'metric.type = "compute.googleapis.com/instance/network/sent_bytes_count" AND '
        'resource.labels.instance_id = "6309067129928439569"'
    )

    resultsCPU = client.list_time_series(
        request={
            "name": project_name,
            "filter": filtroCPU,
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
    )

    resultsNet = client.list_time_series(
        request={
            "name": project_name,
            "filter": filtroNet,
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
    )

    for result in resultsCPU:
        for point in result.points:            
            cpu_gcp = point.value.double_value * 100
            break
    
    for result in resultsNet:
        for point in result.points:
            trafico_gb = (point.value.int64_value)/(1024**3)
    
    precio_hora = 0.08 # Precio de la instancia N2-standart-2
    costo_gcp = (duracion/3600) * precio_hora
    return cpu_gcp, trafico_gb, costo_gcp

def extraerGastosAWS(inicio,fin):
    duracion = int((fin - inicio).total_seconds())
    session = boto3.Session(
        aws_access_key_id="ASIAYWEWXFQRHAY6CTPD", # MODIFICAR
        aws_secret_access_key="m/gH1N+MLbZU/576S6ClUtNLBOMceC23bFMeLfgq", # MODIFICAR
        aws_session_token="IQoJb3JpZ2luX2VjEGQaCXVzLXdlc3QtMiJIMEYCIQC9sSgWA9utgxrqTlyxGY6k2yokb1sj/atK5sOFT4OY+AIhAO8TPQO37iZlg+7KInKpuIZHP09DMJXGLo/ERDEmVRXeKrQCCC0QAhoMNTk3MzE2NTQ1NTcwIgzHb3a6pPUAYxsK+9AqkQK70M+AphJHs61iDgsk7/i9BhKD8hNeTvB5FNXjdrOivtlZKf6JI29BlAiM8/zFtu6WCan5+mOZogEPVPEZlkIhG6nhG1ltKL9QFeEytlfszl/FqDatrcEj4Q5qvo6b13an0qWdaQTjpmhSwwDLCGu4vYVSMkfN+SznovMaGie7P0rioZEL79Izy4G6xrKv6acj7nS2sykIM8Zft8OZRsZOkTvIHcquBzCoUxiOc2Tlq0Da9EvlFGcVSJMO88Do1jzG0ZwnA1gtR+l46xHvwip1JxWbYP+6+ONYbzQJ1RNIGWMKY+ozG8LvzPXFxWdYpMuLlZNHSX7VpZaPZAWAVJMoPbWcfN/WYw8m+eypV5O9SNYwn7/jzgY6nAHz4WxAOpOXEr8Fx0yHTTZBkhY1EhoQZ029xcO7XZkdRgUw2pv1EeaigYEmzSR+RVSmubvH83S7J4CnYQBtYXbdiHYonsco9ZkutmxSpcNKDtbME1C7yKD2prVdqqe6pL2X6Hbn67RF50Cmp751cuSL8ZDdkWJqctIged56/R6jd9oiKjGHHTUDoeF7Bg97Iy3mChi3MwIk8+yGdm0=", #MODIFICAR
        region_name="us-east-1"
        )

    cw = session.client('cloudwatch')

    response = cw.get_metric_statistics(
        Namespace = 'AWS/EC2',
        MetricName = 'CPUUtilization',
        Dimensions = [{'Name': 'InstanceId', 'Value': 'ID'}], #MODIFICAR
        StartTime = inicio,
        EndTime = fin,
        Period = duracion,
        Statistics = ['Average']        
    )   

    responseNet = cw.get_metric_statistics(
        Namespace = 'AWS/EC2',
        MetricName = 'NetworkOut',
        Dimensions = [{'Name': 'InstanceId', 'Value': 'ID'}], # MODIFICAR
        StartTime = inicio,
        EndTime = fin,
        Period = duracion,
        Statistics = ['Sum']        
    ) 

    if response['Datapoints']:
        cpu_mensual_aws = response['Datapoints'][0]['Average']
    
    if responseNet['Datapoints']:
        trafico_sal_aws = responseNet['Datapoints'][0]['Sum']

    trafico_gb = trafico_sal_aws/(1024**3)
    precio_hora = 0.096 # Precio minimo de las instancias M5 (Las mas utilizadas por su equilibrio)
    costo_estimado_aws = (duracion/3600)*precio_hora

    return cpu_mensual_aws, trafico_gb, costo_estimado_aws
