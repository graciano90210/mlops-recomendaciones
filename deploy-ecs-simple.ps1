# Script simplificado de despliegue AWS ECS
Write-Host "Desplegando API MLOps en AWS ECS Fargate..." -ForegroundColor Blue

# Variables
$REGION = "us-east-1"
$CLUSTER_NAME = "mlops-cluster"

# 1. Crear cluster
Write-Host "Paso 1: Creando cluster ECS..." -ForegroundColor Blue
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $REGION

# 2. Crear log group
Write-Host "Paso 2: Configurando CloudWatch Logs..." -ForegroundColor Blue
aws logs create-log-group --log-group-name "/ecs/mlops-recomendaciones" --region $REGION

# 3. Registrar task definition
Write-Host "Paso 3: Registrando Task Definition..." -ForegroundColor Blue
aws ecs register-task-definition --cli-input-json file://aws-ecs-task-definition.json --region $REGION

Write-Host "Task Definition registrada exitosamente!" -ForegroundColor Green
Write-Host "Ahora puedes crear el servicio en la consola AWS ECS" -ForegroundColor Yellow