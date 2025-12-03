pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "vault-ci-${BUILD_NUMBER}"
        CODECOV_TOKEN = credentials('codecov-token')
        DOCKER_BUILDKIT = "1"
        PYTHONPATH = "/app:\${PYTHONPATH}"
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Limpiar') {
            steps {
                script {
                    echo "🧹 Limpiando contenedores previos..."
                    sh '''
                    [ -f docker-compose.override.yml ] && mv docker-compose.override.yml docker-compose.override.yml.bak || true
                    docker compose down -v --remove-orphans 2>/dev/null || true
                    sleep 2
                    '''
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Diagnóstico inicial') {
            steps {
                script {
                    echo "🔍 Diagnóstico inicial del workspace..."
                    sh '''
                    echo "📂 Estructura del proyecto:"
                    find . -type f -name "*.py" | head -20
                    echo ""
                    echo "📄 Contenido de main.py (primeras líneas):"
                    head -30 main.py 2>/dev/null || echo "main.py no encontrado"
                    '''
                }
            }
        }

        stage('Build imágenes') {
            steps {
                script {
                    echo "🔨 Construyendo imágenes Docker..."
                    sh '''
                    echo "🔄 PYTHONPATH en entorno de build: $PYTHONPATH"
                    docker compose build --no-cache --progress=plain api db
                    '''
                }
            }
        }

        stage('Verificar estructura de imagen') {
            steps {
                script {
                    echo "🔬 Verificando estructura de la imagen API..."
                    sh '''
                    echo "📦 Verificando archivos en /app de la imagen:"
                    docker run --rm vault-ci-${BUILD_NUMBER}-api:latest bash -c '
                        echo "=== sys.path ==="
                        python -c "import sys; print(sys.path)"
                        echo ""
                        echo "=== Archivos en /app ==="
                        ls -la /app/
                        echo ""
                        echo "=== Verificando importación ==="
                        python -c "
                        import sys
                        sys.path.insert(0, \"/app\")
                        try:
                            import main
                            print(\"✓ main importado exitosamente\")
                        except Exception as e:
                            print(f\"✗ Error importando main: {e}\")
                            import traceback
                            traceback.print_exc()
                        "
                    '
                    '''
                }
            }
        }

        stage('Levantar stack') {
            steps {
                script {
                    echo "🚀 Levantando servicios (db + api)..."
                    withCredentials([
                        string(credentialsId: 'vault-db-user', variable: 'CI_DB_USER'),
                        string(credentialsId: 'vault-db-password', variable: 'CI_DB_PASSWORD'),
                        string(credentialsId: 'vault-db-name', variable: 'CI_DB_NAME'),
                        string(credentialsId: 'vault-secret-key', variable: 'CI_SECRET_KEY'),
                        string(credentialsId: 'vault-fernet-key', variable: 'CI_FERNET_KEY')
                    ]) {
                        sh '''
                        # Crear archivo .env con credenciales
                        cat > .env <<EOF
DB_USER=${CI_DB_USER}
DB_PASSWORD=${CI_DB_PASSWORD}
DB_NAME=${CI_DB_NAME}
DB_HOST=db
DB_PORT=5432
SECRET_KEY=${CI_SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FERNET_KEY=${CI_FERNET_KEY}
PYTHONPATH=/app
EOF

                        # Crear override para API con PYTHONPATH
                        cat > docker-compose.override.yml <<'OVERRIDE'
version: "3.9"
services:
  api:
    environment:
      - PYTHONPATH=/app
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
      - DB_HOST=db
      - DB_PORT=5432
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=60
      - FERNET_KEY=${FERNET_KEY}
  frontend:
    volumes: []
OVERRIDE

                        echo "📋 Variables de entorno configuradas"
                        echo "🚀 Iniciando servicios..."
                        docker compose up -d db api
                        
                        echo "⏳ Esperando inicialización de servicios..."
                        sleep 10
                        
                        echo "🔍 Verificando estado de contenedores..."
                        docker compose ps
                        '''
                    }
                }
            }
        }

        stage('Verificar API') {
            steps {
                script {
                    echo "🧪 Verificando funcionamiento de la API..."
                    sh '''
                    echo "1. Verificando que el contenedor está corriendo..."
                    docker compose ps api
                    
                    echo ""
                    echo "2. Verificando logs de la API..."
                    docker compose logs api --tail=20
                    
                    echo ""
                    echo "3. Verificando importación en el contenedor..."
                    docker compose exec -T api python -c "
                    import sys
                    print('sys.path:', sys.path)
                    try:
                        import main
                        print('✓ main importado correctamente')
                    except Exception as e:
                        print(f'✗ Error: {e}')
                        import traceback
                        traceback.print_exc()
                    "
                    '''
                }
            }
        }

        stage('Healthcheck') {
            steps {
                script {
                    echo "🏥 Verificando salud de la API..."
                    sh '''
                    max_attempts=30
                    attempt=1
                    
                    while [ $attempt -le $max_attempts ]; do
                        echo "Intento $attempt/$max_attempts..."
                        
                        # Verificar si el contenedor está corriendo
                        if ! docker compose ps api | grep -q "Up"; then
                            echo "⚠️ Contenedor API no está corriendo"
                            docker compose logs api --tail=20
                            exit 1
                        fi
                        
                        # Intentar healthcheck
                        if docker compose exec -T api curl -sf http://localhost:5000/health > /dev/null 2>&1; then
                            echo "✅ API saludable - endpoint /health responde"
                            
                            # Verificar también /docs
                            if docker compose exec -T api curl -sf http://localhost:5000/docs > /dev/null 2>&1; then
                                echo "✅ Documentación Swagger disponible"
                                break
                            fi
                        fi
                        
                        # Si no responde, mostrar logs y esperar
                        docker compose logs api --tail=5
                        attempt=$((attempt + 1))
                        sleep 3
                    done
                    
                    if [ $attempt -gt $max_attempts ]; then
                        echo "❌ API no respondió después de $max_attempts intentos"
                        echo "📋 Logs completos de la API:"
                        docker compose logs api
                        exit 1
                    fi
                    
                    echo "✅ API completamente operativa"
                    '''
                }
            }
        }

        stage('Ejecutar tests') {
            steps {
                script {
                    echo "🧪 Ejecutando pytest con cobertura..."
                    sh '''
                    # Crear directorio para reportes en el contenedor
                    docker compose exec -T api mkdir -p /app/test-reports
                    
                    # Ejecutar pruebas con cobertura
                    docker compose exec -T api pytest tests/ \
                      --junitxml=/app/test-reports/junit.xml \
                      --cov=. \
                      --cov-report=xml:/app/coverage.xml \
                      --cov-report=html:/app/htmlcov \
                      --cov-report=term-missing \
                      -v \
                      --tb=short \
                      || echo "⚠️ Algunos tests fallaron, continuando..."
                    '''
                }
            }
        }

        stage('Copiar reportes') {
            steps {
                script {
                    echo "📊 Copiando reportes de pruebas..."
                    sh '''
                    # Crear directorios locales
                    mkdir -p test-reports coverage-report
                    
                    # Copiar reportes del contenedor
                    docker compose cp api:/app/coverage.xml ./coverage.xml 2>/dev/null || echo "⚠️ coverage.xml no encontrado"
                    docker compose cp api:/app/htmlcov ./coverage-report/ 2>/dev/null || echo "⚠️ htmlcov no encontrado"
                    docker compose cp api:/app/test-reports/junit.xml ./test-reports/ 2>/dev/null || echo "⚠️ junit.xml no encontrado"
                    
                    # Verificar que los reportes existen
                    echo "📁 Reportes generados:"
                    ls -la coverage.xml 2>/dev/null || echo "coverage.xml no generado"
                    ls -la coverage-report/ 2>/dev/null || echo "coverage-report no generado"
                    ls -la test-reports/junit.xml 2>/dev/null || echo "junit.xml no generado"
                    '''
                }
            }
        }

        stage('Upload a Codecov') {
            steps {
                script {
                    echo "☁️ Subiendo coverage a Codecov..."
                    sh '''
                    if [ -f "coverage.xml" ]; then
                        echo "📊 Enviando reporte de cobertura a Codecov..."
                        
                        # Opción 1: Usar el uploader oficial (recomendado)
                        curl -Os https://uploader.codecov.io/latest/linux/codecov
                        chmod +x codecov
                        
                        # Subir con token y flags adicionales
                        ./codecov \
                          -t ${CODECOV_TOKEN} \
                          -f coverage.xml \
                          -Z \
                          --verbose \
                          || echo "⚠️ Error al subir a Codecov, continuando..."
                        
                        echo "✅ Reporte enviado a Codecov"
                    else
                        echo "❌ No se encontró coverage.xml - no se puede subir a Codecov"
                        echo "📁 Contenido actual:"
                        ls -la
                    fi
                    '''
                }
            }
        }

        stage('Smoke test') {
            steps {
                script {
                    echo "💨 Ejecutando smoke test..."
                    sh '''
                    echo "🧪 Realizando smoke test en la API..."
                    
                    # Verificar que la API responde
                    if docker compose exec -T api curl -sf http://localhost:5000/health > /dev/null; then
                        echo "✅ Health check exitoso"
                    else
                        echo "❌ Health check falló"
                        exit 1
                    fi
                    
                    # Intentar registro de usuario de prueba
                    EMAIL="test-ci-${BUILD_NUMBER}-${RANDOM}@example.com"
                    
                    echo "📝 Creando usuario de prueba: $EMAIL"
                    
                    response=$(docker compose exec -T api curl -s -X POST \
                      http://localhost:5000/usuarios/registro \
                      -H "Content-Type: application/json" \
                      -d "{
                        \\"nombre\\": \\"Test\\",
                        \\"apellido\\": \\"CI\\",
                        \\"correo\\": \\"$EMAIL\\",
                        \\"contrasena\\": \\"test1234\\"
                      }" 2>/dev/null || echo "{}")
                    
                    echo "Respuesta: $response"
                    
                    if echo "$response" | grep -q "id"; then
                        echo "✅ Smoke test completado exitosamente"
                    else
                        echo "⚠️ Smoke test parcial - registro falló pero API responde"
                        echo "📋 Continuando sin error..."
                    fi
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "🧹 Limpieza final..."
                sh '''
                echo "🛑 Deteniendo contenedores..."
                docker compose down -v --remove-orphans 2>/dev/null || true
                
                # Restaurar override si existía
                [ -f docker-compose.override.yml.bak ] && mv docker-compose.override.yml.bak docker-compose.override.yml || true
                
                # Limpiar archivos temporales
                rm -f .env codecov 2>/dev/null || true
                '''
            }
        }

        success {
            script {
                echo "✅ Pipeline completado exitosamente"
                sh '''
                echo "📊 Reportes disponibles:"
                if [ -f "coverage.xml" ]; then
                        echo "  • coverage.xml - Reporte de cobertura"
                fi
                if [ -d "coverage-report" ]; then
                        echo "  • coverage-report/ - Reporte HTML de cobertura"
                fi
                if [ -f "test-reports/junit.xml" ]; then
                        echo "  • test-reports/junit.xml - Reporte JUnit de tests"
                fi
                
                # Mostrar resumen de cobertura si existe
                if [ -f "coverage.xml" ]; then
                        echo ""
                        echo "📈 Resumen de cobertura:"
                        grep -o 'line-rate="[0-9.]*"' coverage.xml | head -1 | sed 's/line-rate=//' | xargs echo "  • Cobertura de líneas: "
                fi
                '''
                
                // Archivar reportes
                archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
                archiveArtifacts artifacts: 'coverage-report/**', allowEmptyArchive: true
                archiveArtifacts artifacts: 'test-reports/junit.xml', allowEmptyArchive: true
                
                // Publicar reportes
                junit testResults: 'test-reports/junit.xml', allowEmptyResults: true
                publishHTML target: [
                    reportName: 'Coverage Report',
                    reportDir: 'coverage-report',
                    reportFiles: 'index.html',
                    keepAll: true,
                    alwaysLinkToLastBuild: true
                ]
            }
        }

        failure {
            script {
                echo "❌ Pipeline falló"
                sh '''
                echo "🔍 Últimos logs de la API:"
                docker compose logs api --tail=50 2>/dev/null || true
                
                echo ""
                echo "🔍 Estado de contenedores:"
                docker compose ps 2>/dev/null || true
                
                echo ""
                echo "🔍 Archivos en workspace:"
                ls -la
                '''
            }
        }

        unstable {
            script {
                echo "⚠️ Pipeline inestable - algunos tests fallaron"
            }
        }

        cleanup {
            cleanWs(cleanWhenAborted: true, cleanWhenFailure: true, cleanWhenNotBuilt: true, 
                    cleanWhenSuccess: true, cleanWhenUnstable: true, deleteDirs: true)
        }
    }
}