# ***************** Universidad de los Andes ***********************
# ****** Departamento de Ingeniería de Sistemas y Computación ******
# ********** Arquitectura y diseño de Software - ISIS2503 **********
#
# Infraestructura para laboratorio de Circuit Breaker
#
# Elementos a desplegar en AWS:
# 1. Grupos de seguridad:
#    - cbd-traffic-django (puerto 8080)
#    - cbd-traffic-cb (puertos 8000 y 8001)
#    - cbd-traffic-db (puerto 5432)
#    - cbd-traffic-ssh (puerto 22)
#
# 2. Instancias EC2:
#    - cbd-kong
#    - cbd-db (PostgreSQL instalado y configurado)
#    - cbd-monitoring (Monitoring app instalada y migraciones aplicadas)
#    - cbd-alarms-a (Monitoring app instalada)
#    - cbd-alarms-b (Monitoring app instalada)
#    - cbd-alarms-c (Monitoring app instalada)
# ******************************************************************

# Variable. Define la región de AWS donde se desplegará la infraestructura.
variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

# Variable. Define el prefijo usado para nombrar los recursos en AWS.
variable "project_prefix" {
  description = "Prefix used for naming AWS resources"
  type        = string
  default     = "cbd"
}

# Variable. Define el tipo de instancia EC2 a usar para las máquinas virtuales.
variable "instance_type" {
  description = "EC2 instance type for application hosts"
  type        = string
  default     = "t2.nano"
}

# Proveedor. Define el proveedor de infraestructura (AWS) y la región.
provider "aws" {
  region = var.region
}

# Variables locales usadas en la configuración de Terraform.
locals {
  project_name = "${var.project_prefix}-circuit-breaker"
  repository   = "https://github.com/ISIS2503/ISIS2503-MonitoringApp.git"
  branch       = "Circuit-Breaker"

  common_tags = {
    Project   = local.project_name
    ManagedBy = "Terraform"
  }
}

# Data Source. Busca la AMI más reciente de Ubuntu 24.04 usando los filtros especificados.
data "aws_ami" "ubuntu" {
    most_recent = true
    owners      = ["099720109477"]

    filter {
        name   = "name"
        values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
    }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }
}

data "aws_security_group" "sg_ssh" {
  name = "cbd-traffic-ssh"
}
data "aws_security_group" "sg_dj" {
  name = "cbd-traffic-django"
}
data "aws_instance" "database" {
  filter {
    name   = "tag:Name"
    values = ["cbd-db"]
  }
}

# Recurso. Define la instancia EC2 para la aplicación de Monitoring (Django).
# Esta instancia incluye un script de creación para instalar la aplicación de Monitoring y aplicar las migraciones.
resource "aws_instance" "monitoring" {
  for_each = toset(["b", "c"])
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [data.aws_security_group.sg_dj.id, data.aws_security_group.sg_ssh.id]

  user_data = <<-EOT
              #!/bin/bash

              echo "DATABASE_HOST=${data.aws_instance.database.private_ip}" | sudo tee -a /etc/environment

              sudo apt-get update -y
              sudo apt-get install -y python3-pip git build-essential libpq-dev python3-dev

              mkdir -p /labs
              cd /labs

              if [ ! -d ISIS2503-MonitoringApp ]; then
                git clone ${local.repository}
              fi

              cd ISIS2503-MonitoringApp
              git fetch origin ${local.branch}
              git checkout ${local.branch}
              sudo pip3 install --upgrade pip --break-system-packages
              sudo pip3 install -r requirements.txt --break-system-packages

              sudo python3 manage.py makemigrations
              sudo python3 manage.py migrate
              EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-monitoring-${each.key}"
    Role = "monitoring-app"
  })
}

output "monitoring_public_ips" {
  value = { for id, instance in aws_instance.monitoring : id => instance.public_ip }
}

