pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "vault-ci-${BUILD_NUMBER}"
        CODECOV_TOKEN = credentials('codecov-token')
        DOCKER_BUILDKIT = "1"
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

        stage('Build imágenes') {
            steps {
                script {
                    echo "🔨 Construyendo imágenes Docker..."
                    sh '''
                    docker compose build --no-cache api db
                    '''
                }
            }
        }

        stage('Inspeccionar imagen') {
            steps {
                script {
                    echo "🔬 Inspeccionando imagen de API antes de levantar..."
                    sh '''
                    echo "📦 Archivos en /app de la imagen api:"
                    docker run --rm vault-ci-${BUILD_NUMBER}-api:latest ls -la /app/ || true
                    
                    echo ""
                    echo "📄 Primeras líneas de main.py:"
                    docker run --rm vault-ci-${BUILD_NUMBER}-api:latest head -20 /app/main.py || echo "❌ main.py no encontrado en imagen"
                    
                    echo ""
                    echo "⚙️ CMD de la imagen:"
                    docker inspect vault-ci-${BUILD_NUMBER}-api:latest | grep -A 3 '"Cmd"'
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
EOF

                        cat > docker-compose.override.yml <<'OVERRIDE'
version: "3.9"
services:
  api:
    volumes:
      - /app:/app
  frontend:
    volumes: []
OVERRIDE

                        docker compose up -d db api
                        echo "⏳ Esperando a que la BD esté lista..."
                        sleep 8
                        '''
                    }
                }
            }
        }

        stage('Diagnosticar') {
            steps {
                script {
                    echo "🔍 Diagnosticando contenedor de la API..."
                    sh '''
                    echo "📁 Archivos en /app del contenedor:"
                    docker compose exec -T api ls -la /app/ || true
                    
                    echo ""
                    echo "🐍 Verificando que Python puede importar main:"
                    docker compose exec -T api python -c "import sys; sys.path.insert(0, '/app'); import main; print('✓ main importado exitosamente')" || echo "⚠️ Fallo al importar main"
                    
                    echo ""
                    echo "📋 Logs del contenedor api:"
                    docker compose logs api --tail=50 || true
                    '''
                }
            }
        }

        stage('Healthcheck') {
            steps {
                script {
                    echo "🏥 Verificando salud de la API..."
                    sh '''
                    echo "⏳ Esperando 15 segundos antes de healthcheck..."
                    sleep 15
                    
                    max_attempts=30
                    attempt=1
                    
                    while [ $attempt -le $max_attempts ]; do
                        if docker compose exec -T api curl -sf http://localhost:5000/docs > /dev/null 2>&1; then
                            echo "✓ API está saludable en intento $attempt"
                            exit 0
                        fi
                        
                        echo "Intento $attempt/$max_attempts: API no lista..."
                        docker compose logs api --tail=3
                        
                        attempt=$((attempt + 1))
                        sleep 2
                    done
                    
                    echo "✗ API no respondió después de $max_attempts intentos"
                    echo ""
                    echo "📋 Logs completos de la API:"
                    docker compose logs api
                    exit 1
                    '''
                }
            }
        }

        stage('Ejecutar tests') {
            steps {
                script {
                    echo "🧪 Ejecutando pytest con cobertura..."
                    sh '''
                    docker compose exec -T api pytest \
                      --cov=. \
                      --cov-report=xml \
                      --cov-report=html \
                      --cov-report=term-missing \
                      -v \
                      --tb=short
                    '''
                }
            }
        }

        stage('Copiar reportes') {
            steps {
                script {
                    echo "📊 Copiando reportes..."
                    sh '''
                    mkdir -p coverage htmlcov
                    docker compose cp api:/app/coverage.xml ./coverage.xml || true
                    docker compose cp api:/app/htmlcov ./htmlcov || true
                    '''
                }
            }
        }

        stage('Upload a Codecov') {
            steps {
                script {
                    echo "☁️ Subiendo coverage a Codecov..."
                    sh '''
                    if [ -f coverage.xml ]; then
                        curl -Os https://uploader.codecov.io/latest/linux/codecov
                        chmod +x codecov
                        ./codecov -t ${CODECOV_TOKEN} -f coverage.xml || true
                    else
                        echo "⚠️ No se encontró coverage.xml"
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
                    EMAIL="ci-${BUILD_NUMBER}-${RANDOM}@example.com"
                    
                    response=$(docker compose exec -T api curl -s -X POST \
                      http://localhost:5000/usuarios/registro \
                      -H "Content-Type: application/json" \
                      -d "{
                        \\"nombre\\": \\"CI\\",
                        \\"apellido\\": \\"User\\",
                        \\"correo\\": \\"$EMAIL\\",
                        \\"contrasena\\": \\"ci1234\\"
                      }")
                    
                    if echo "$response" | grep -q "id"; then
                        echo "✓ Smoke test pasó: usuario registrado exitosamente"
                    else
                        echo "✗ Smoke test falló: $response"
                        exit 1
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
                docker compose down -v --remove-orphans || true
                [ -f docker-compose.override.yml.bak ] && mv docker-compose.override.yml.bak docker-compose.override.yml || true
                '''
            }
        }

        success {
            script {
                echo "✅ Pipeline completado exitosamente"
                sh '''
                if [ -d "htmlcov" ]; then
                    echo "📊 Coverage report disponible en ./htmlcov/index.html"
                fi
                '''
            }
        }

        failure {
            script {
                echo "❌ Pipeline falló"
                sh '''
                echo "Últimos logs de la API:"
                docker compose logs api --tail=50 || true
                '''
            }
        }

        unstable {
            script {
                echo "⚠️ Pipeline inestable - revisar logs"
            }
        }

        cleanup {
            cleanWs()
        }
    }
}