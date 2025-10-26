# 🚀 Script de Despliegue en AWS ECS Fargate
# =========================================

param(
    [string]$ClusterName = "mlops-cluster",
    [string]$ServiceName = "mlops-recomendaciones-service",
    [string]$TaskDefinition = "mlops-recomendaciones-task",
    [string]$SubnetIds = "",  # Comma-separated subnet IDs
    [string]$SecurityGroupId = ""
)

Write-Host "🚀 Desplegando API MLOps en AWS ECS Fargate..." -ForegroundColor Blue
Write-Host "=============================================" -ForegroundColor Blue

# Variables
$REGION = "us-east-1"
$ACCOUNT_ID = "322614675421"
$IMAGE_URI = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/mlops-recomendaciones:latest"

Write-Host "📋 Configuración:" -ForegroundColor Yellow
Write-Host "  Cluster: $ClusterName"
Write-Host "  Service: $ServiceName"
Write-Host "  Task Definition: $TaskDefinition"
Write-Host "  Image: $IMAGE_URI"

# 1. Crear cluster si no existe
Write-Host "`n🏗️ Paso 1: Creando cluster ECS..." -ForegroundColor Blue
try {
    aws ecs describe-clusters --clusters $ClusterName --region $REGION 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Creando nuevo cluster..." -ForegroundColor Yellow
        aws ecs create-cluster --cluster-name $ClusterName --region $REGION
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Cluster creado exitosamente" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Error creando cluster" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  ✅ Cluster ya existe" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Error verificando cluster: $_" -ForegroundColor Red
    exit 1
}

# 2. Crear log group si no existe
Write-Host "`n📝 Paso 2: Configurando CloudWatch Logs..." -ForegroundColor Blue
try {
    aws logs describe-log-groups --log-group-name-prefix "/ecs/mlops-recomendaciones" --region $REGION 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Creando log group..." -ForegroundColor Yellow
        aws logs create-log-group --log-group-name "/ecs/mlops-recomendaciones" --region $REGION
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Log group creado exitosamente" -ForegroundColor Green
        }
    } else {
        Write-Host "  ✅ Log group ya existe" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️ Advertencia configurando logs: $_" -ForegroundColor Yellow
}

# 3. Registrar task definition
Write-Host "`n📦 Paso 3: Registrando Task Definition..." -ForegroundColor Blue
try {
    $taskDefResult = aws ecs register-task-definition --cli-input-json file://aws-ecs-task-definition.json --region $REGION
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Task Definition registrada exitosamente" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Error registrando Task Definition" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ Error registrando Task Definition: $_" -ForegroundColor Red
    exit 1
}

# 4. Crear o actualizar servicio
Write-Host "`n🚀 Paso 4: Configurando servicio ECS..." -ForegroundColor Blue

if ([string]::IsNullOrEmpty($SubnetIds) -or [string]::IsNullOrEmpty($SecurityGroupId)) {
    Write-Host "  ⚠️ Se necesitan SubnetIds y SecurityGroupId para crear el servicio" -ForegroundColor Yellow
    Write-Host "  💡 Puedes obtenerlos con:" -ForegroundColor Yellow
    Write-Host "    aws ec2 describe-subnets --region $REGION"
    Write-Host "    aws ec2 describe-security-groups --region $REGION"
    Write-Host ""
    Write-Host "  📦 Task Definition registrada. Puedes crear el servicio manualmente en la consola AWS." -ForegroundColor Blue
} else {
    try {
        # Verificar si el servicio existe
        aws ecs describe-services --cluster $ClusterName --services $ServiceName --region $REGION 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Actualizando servicio existente..." -ForegroundColor Yellow
            aws ecs update-service --cluster $ClusterName --service $ServiceName --task-definition $TaskDefinition --region $REGION
        } else {
            Write-Host "  Creando nuevo servicio..." -ForegroundColor Yellow
            $networkConfig = @{
                awsvpcConfiguration = @{
                    subnets = $SubnetIds.Split(',')
                    securityGroups = @($SecurityGroupId)
                    assignPublicIp = "ENABLED"
                }
            } | ConvertTo-Json -Depth 10
            
            aws ecs create-service --cluster $ClusterName --service-name $ServiceName --task-definition $TaskDefinition --desired-count 1 --launch-type FARGATE --network-configuration $networkConfig --region $REGION
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Servicio configurado exitosamente" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Error configurando servicio" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ Error configurando servicio: $_" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Despliegue completado!" -ForegroundColor Green
Write-Host "🌐 Tu API estará disponible en la IP pública del servicio ECS" -ForegroundColor Yellow
Write-Host "📊 Monitorea el estado en:" -ForegroundColor Blue
Write-Host "  - AWS ECS Console: https://console.aws.amazon.com/ecs/"
Write-Host "  - CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logs:"

Write-Host "`n🛠️ Comandos útiles:" -ForegroundColor Blue
Write-Host "  # Ver servicios:"
Write-Host "  aws ecs list-services --cluster $ClusterName --region $REGION"
Write-Host ""
Write-Host "  # Ver tareas:"
Write-Host "  aws ecs list-tasks --cluster $ClusterName --region $REGION"
Write-Host ""
Write-Host "  # Ver logs:"
Write-Host "  aws logs tail /ecs/mlops-recomendaciones --follow --region $REGION"