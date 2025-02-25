pipeline {
    agent {
        label 'cfsw_gen2_builder'
    }
    options {
        disableConcurrentBuilds()
    }
    environment {
        MASTER_BRANCH = "main"
        INFRA_BRANCH = 'infra'
        SERVICE_BRANCH_PREFIX = "sv"
        AUTO_TEST_COMPOSE_FILE = "auto-test.yml"
        PROD_COMPOSE_FILE = "docker-compose.prod.yml"
        DEPLOY_SINGLE_FILE = "docker-compose.test.yml"
        PROJECT_ENV_FILE = "project.env"
        DOCKER_REGISTRY = "docker.io"
        DOCKER_CRED = credentials('docker-hub-token')
    }
    stages {
        stage('Prebuild') {
            steps {
                script {
                    if (env.BRANCH_NAME.startsWith(SERVICE_BRANCH_PREFIX)) {
                        env.SERVICE = env.BRANCH_NAME.replaceFirst("${SERVICE_BRANCH_PREFIX}/", "")
                        env.TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
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
                    sh "docker-compose -f ${PROD_COMPOSE_FILE} --env-file ${PROJECT_ENV_FILE} build"
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
                    sh "docker-compose -f ${PROD_COMPOSE_FILE} --env-file ${PROJECT_ENV_FILE} up -d --remove-orphans"
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
                    sh "docker-compose -f ${AUTO_TEST_COMPOSE_FILE} --profile allservice up"
                    def numOfTestFailed = checkTestContainersExitCode()
                    if (numOfTestFailed != 0) {
                        error("Automation Test Failed!")
                    }
                }
            }
            post {
                always {
                    script {
                        sh """
                            docker-compose -f ${AUTO_TEST_COMPOSE_FILE} --profile allservice down
                            docker-compose -f ${PROD_COMPOSE_FILE} --env-file ${PROJECT_ENV_FILE} down
                            sleep 5
                        """
                    }
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
                    sh "docker build -t ${env.SERVICE}:latest services/${env.SERVICE}/src"
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
                    sh "docker-compose -f ${DEPLOY_SINGLE_FILE} --env-file ${PROJECT_ENV_FILE} --profile db --profile event-bus --profile ${env.SERVICE} up -d --remove-orphans"
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
                    sh "docker-compose -f ${AUTO_TEST_COMPOSE_FILE} --profile ${env.SERVICE} up"
                    def numOfTestFailed = checkTestContainersExitCode()
                    if (numOfTestFailed != 0) {
                        error("Automation Test Failed!")
                    }
                }
            }
            post {
                always {
                    script {
                        sh """
                            docker-compose -f ${DEPLOY_SINGLE_FILE} --env-file ${PROJECT_ENV_FILE} --profile db --profile event-bus --profile ${env.SERVICE} down
                            docker-compose -f ${AUTO_TEST_COMPOSE_FILE} --profile db --profile ${env.SERVICE} down
                            sleep 5
                        """
                    }
                }
            }
        }
        stage('Release ${env.SERVICE} Service') {
            when {
                branch "${env.SERVICE_BRANCH_PREFIX}/*"
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-token', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        def tagCurrentCommit = "${DOCKER_USER}/${env.SERVICE}:${env.TAG}"
                        def tagLatest = "${DOCKER_USER}/${env.SERVICE}:latest"
                        echo "Logging into Docker Registry..."
                        sh "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin ${DOCKER_REGISTRY}"
                        echo "Tagging and pushing Docker images..."
                        sh """
                            docker tag ${env.SERVICE}:latest ${tagLatest}
                            docker tag ${env.SERVICE}:latest ${tagCurrentCommit}
                            docker push ${tagCurrentCommit}
                            docker push ${tagLatest}
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                echo "Cleaning up Docker resources..."
                sh '''
                    docker system prune -a -f
                    sleep 5
                '''
                cleanWs()
            }
        }
    }
}

def checkTestContainersExitCode() {
    def containers = sh(script: '''docker ps -a --format '{{.Names}}' | grep '_test$' ''', returnStdout: true).trim().split('\n')
    def failedServices = []
    containers.each { container ->
        def exitCode = sh(script: "docker wait ${container}", returnStdout: true).trim()
        if (exitCode != '0') {
            failedServices << container
            echo "${container} failed!"
        }
    }
    return failedServices.size()
}
