pipeline {
    agent {
        label 'cfsw_gen2_builder'
    }
    environment {
        MASTER_BRANCH = "main"
        INFRA_BRANCH = 'infra'
        SERVICE_BRANCH_PREFIX = "sv"
        AUTO_TEST_COMPOSE_FILE = "auto-test.yml"
        TAG = "1.0"
    }
    stages {
        stage ('Prebuild') {
            steps {
                script {
                    if (env.BRANCH_NAME.startsWith(SERVICE_BRANCH_PREFIX)) {
                        env.SERVICE = env.BRANCH_NAME.replaceFirst("${SERVICE_BRANCH_PREFIX}/", "")
                    }
                }
            }
        }
        stage('Build system') {
            when {
                anyOf {
                    branch "${env.MASTER_BRANCH}"
                    branch "${env.INFRA_BRANCH}"
                    changeRequest()
                }
            }
            steps {
                script {
                    echo "Building system..."
                    sh "docker-compose --profile system build"
                }
            }
        }
        stage('Deploy system') {
            when {
                anyOf {
                    branch "${env.MASTER_BRANCH}"
                    branch "${env.INFRA_BRANCH}"
                    changeRequest()
                }
            }
            steps {
                script {
                    echo "Deploying system..."
                    sh "docker-compose --profile system up -d"
                }
            }
        }
        stage('Test system') {
            when {
                anyOf {
                    branch "${env.MASTER_BRANCH}"
                    branch "${env.INFRA_BRANCH}"
                    changeRequest()
                }
            }
            steps {
                script {
                    sleep(5)
                    echo "Testing all services..."
                    sh "docker-compose -f ${AUTO_TEST_COMPOSE_FILE} --profile allservice up -d"
                }
            }
        }
        stage('Build ${env.SERVICE} Service') {
            when {
                branch "${env.SERVICE_BRANCH_PREFIX}/*"
            }
            steps {
                script {
                    echo "Building ${env.SERVICE} service..."
                    sh "docker build -t ${env.SERVICE}:${env.TAG} services/${env.SERVICE}/src"
                }
            }
        }
        stage('Deploy ${env.SERVICE} Service') {
            when {
                branch "${env.SERVICE_BRANCH_PREFIX}/*"
            }
            steps {
                script {
                    echo "Deploying ${env.SERVICE} service..."
                    sh "docker-compose -f ${AUTO_TEST_COMPOSE_FILE} --profile ${env.SERVICE} up -d"
                }
            }
        }
        stage('Test ${env.SERVICE} Service') {
            when {
                branch "${env.SERVICE_BRANCH_PREFIX}/*"
            }
            steps {
                script {
                    sleep(5)
                    echo "Testing ${env.SERVICE} service..."
                    sh "docker-compose --profile db --profile ${env.SERVICE} up -d"
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
