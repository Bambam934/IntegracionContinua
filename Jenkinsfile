pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "vault-ci-${BUILD_NUMBER}"
        CODECOV_TOKEN = credentials('codecov-token')
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Limpiar') {
            steps {
                sh '''
                [ -f docker-compose.override.yml ] && mv docker-compose.override.yml docker-compose.override.yml.bak || true
                docker compose down -v --remove-orphans 2>/dev/null || true
                sleep 2
                '''
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'docker compose build --no-cache api db'
            }
        }

        stage('Levantar stack') {
            steps {
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
                    docker compose up -d db api
                    sleep 10
                    '''
                }
            }
        }

        stage('Healthcheck') {
            steps {
                sh '''
                max_attempts=20
                attempt=1
                while [ $attempt -le $max_attempts ]; do
                    if docker compose exec -T api curl -sf http://localhost:5000/docs > /dev/null 2>&1; then
                        echo "✓ API healthy"
                        exit 0
                    fi
                    echo "Wait... attempt $attempt/$max_attempts"
                    attempt=$((attempt + 1))
                    sleep 3
                done
                echo "API timeout"
                docker compose logs api
                exit 1
                '''
            }
        }

        stage('Tests') {
            steps {
                sh '''
                docker compose exec -T api pytest \
                  --cov=. \
                  --cov-report=xml \
                  --cov-report=html \
                  --cov-report=term-missing \
                  -v
                '''
            }
        }

        stage('Reportes') {
            steps {
                sh '''
                mkdir -p coverage
                docker compose cp api:/app/coverage.xml ./coverage.xml || true
                docker compose cp api:/app/htmlcov ./htmlcov || true
                '''
            }
        }

        stage('Codecov') {
            steps {
                sh '''
                if [ -f coverage.xml ]; then
                    curl -Os https://uploader.codecov.io/latest/linux/codecov
                    chmod +x codecov
                    ./codecov -t ${CODECOV_TOKEN} -f coverage.xml || true
                fi
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                EMAIL="ci-${BUILD_NUMBER}-${RANDOM}@example.com"
                docker compose exec -T api curl -s -X POST http://localhost:5000/usuarios/registro \
                  -H "Content-Type: application/json" \
                  -d "{\"nombre\":\"CI\",\"apellido\":\"User\",\"correo\":\"$EMAIL\",\"contrasena\":\"ci1234\"}" \
                  | grep -q "id" || exit 1
                '''
            }
        }
    }

    post {
        always {
            sh '''
            docker compose down -v --remove-orphans || true
            [ -f docker-compose.override.yml.bak ] && mv docker-compose.override.yml.bak docker-compose.override.yml || true
            '''
        }

        success {
            echo "✅ Pipeline OK"
        }

        failure {
            sh 'docker compose logs api --tail=30 || true'
        }
    }
}
