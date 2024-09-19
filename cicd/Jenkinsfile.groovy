pipeline {
    agent {
        label 'cfsw_gen2_builder'
    }
    environment {
        MASTER_BRANCH = "main"
        INFRA_BRANCH = 'infra'
        ACCOUNT_BRANCH = "account"
        ORDER_BRANCH = "order"
        LICENSE_BRANCH = "license"
    }
    stages {
        stage('Build Master') {
            when {
                branch env.MASTER_BRANCH
            }
            steps {
                script {
                    echo "Building system..."
                    sh '''
                        docker-compose --profile all build
                    '''
                }
            }
        }
        stage('Test Master') {
            when {
                branch env.MASTER_BRANCH
            }
            steps {
                script {
                    echo "Running all tests..."
                }
            }
        }
        stage('Build Account Service') {
            when {
                branch env.ACCOUNT_BRANCH
            }
            steps {
                script {
                    echo "Building account service..."
                    sh '''
                        docker-compose --profile account build
                    '''
                }
            }
        }
        stage('Test Service') {
            when {
                branch env.DEV_BRANCH
            }
            steps {
                script {
                    echo "Testing  service..."
                }
            }
        }
    }
    post {
        always {
            script {
                // Clean up Docker containers, networks, volumes, and images created by Docker Compose
                echo "Cleaning up Docker resources..."
                sh '''
                    docker-compose down --volumes --remove-orphans
                    docker system prune -f --volumes
                '''
                cleanWs()
            }
        }
    }
}
