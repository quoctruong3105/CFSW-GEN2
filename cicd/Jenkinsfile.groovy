pipeline {
    agent {
        label 'cfsw_gen2_builder'
    }
    environment {
        MASTER_BRANCH = "main"
        INFRA_BRANCH = 'infra'
        ACCOUNT_BRANCH = "account"
        ORDER_BRANCH = "order"
        AUTHORIZE_BRANCH = "authorize"
    }
    stages {
        stage('Build system') {
            when {
                anyOf {
                    branch env.MASTER_BRANCH
                    branch env.INFRA_BRANCH
                }
            }
            steps {
                script {
                    echo "Building system..."
                    sh 'docker-compose --profile system build'
                }
            }
        }
        stage('Deploy system') {
            when {
                anyOf {
                    branch env.MASTER_BRANCH
                    branch env.INFRA_BRANCH
                }
            }
            steps {
                script {
                    echo "Deploying system..."
                    sh 'docker-compose --profile system up -d'
                }
            }
        }
        stage('Test system') {
            when {
                anyOf {
                    branch env.MASTER_BRANCH
                    branch env.INFRA_BRANCH
                }
            }
            steps {
                script {
                    sleep(5)
                    echo "Testing all services..."
                    sh 'docker-compose -f auto-test.yml --profile allservice up'
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
                    sh 'docker build -t account:1.0 services/account/src'
                }
            }
        }
        stage('Deploy Account Service') {
            when {
                branch env.ACCOUNT_BRANCH
            }
            steps {
                script {
                    echo "Deploying Account service..."
                    sh 'docker-compose -f auto-test.yml --profile account up -d'
                }
            }
        }
        stage('Test Account Service') {
            when {
                branch env.ACCOUNT_BRANCH
            }
            steps {
                script {
                    sleep(5)
                    echo "Testing Account service..."
                    sh 'docker-compose --profile db -- profile account up'
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
                    docker-compose -f auto-test.yml down
                    docker-compose down
                    docker system prune -a -f
                '''
                cleanWs()
            }
        }
    }
}
