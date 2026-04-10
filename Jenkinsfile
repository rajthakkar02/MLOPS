pipeline {

    agent any

    environment {
        COMPOSE_FILE = "docker-compose.yml"
    }

    stages {

        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/rajthakkar02/MLOPS.git', branch: 'main'
            }
        }

        stage('Build Docker Images') {
            steps {
                bat 'docker compose build'
            }
        }

        stage('Stop Existing Containers') {
            steps {
                bat 'docker compose down || exit 0'
            }
        }

        stage('Deploy Containers') {
            steps {
                bat 'docker compose up -d'
            }
        }

        stage('Check Running Containers') {
            steps {
                bat 'docker ps'
            }
        }

    }

    post {

        success {
            echo 'Deployment Successful'
        }

        failure {
            echo 'Deployment Failed'
        }

        always {
            cleanWs()
        }

    }

}