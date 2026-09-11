pipeline {

    agent any

    environment {
        APP_DIR = "/opt/docker-fastapi-react-mysql"
        COMPOSE_FILE = "docker-compose.yml"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }


        stage('Sync Code') {
            steps {

                sh '''
                    set -e

                    rsync -av --delete \
                        --exclude=".env" \
                        --exclude=".git" \
                        "$WORKSPACE/" \
                        "$APP_DIR/"
                '''
            }
        }


        stage('Validate Compose') {
            steps {

                sh '''
                    set -e

                    cd "$APP_DIR"

                    docker compose \
                        -f "$COMPOSE_FILE" \
                        config
                '''
            }
        }


        stage('Build Images') {
            steps {

                sh '''
                    set -e

                    cd "$APP_DIR"

                    docker compose \
                        -f "$COMPOSE_FILE" \
                        build
                '''
            }
        }


        stage('Deploy') {
            steps {

                sh '''
                    set -e

                    cd "$APP_DIR"

                    docker compose \
                        -f "$COMPOSE_FILE" \
                        up -d
                '''
            }
        }


        stage('Wait For Services') {
            steps {

                sh '''
                    set -e

                    sleep 15

                    cd "$APP_DIR"

                    docker compose \
                        -f "$COMPOSE_FILE" \
                        ps
                '''
            }
        }


        stage('Health Check') {
            steps {

                sh '''
                    set -e

                    curl -f http://localhost/
                    curl -f http://localhost/api/docs

                    echo "Application is healthy"
                '''
            }
        }
    }


    post {

        failure {

            sh '''
                cd "$APP_DIR"

                echo "===== CONTAINER STATUS ====="

                docker compose \
                    -f "$COMPOSE_FILE" \
                    ps

                echo "===== CONTAINER LOGS ====="

                docker compose \
                    -f "$COMPOSE_FILE" \
                    logs --tail=30
            '''
        }
    }
}
