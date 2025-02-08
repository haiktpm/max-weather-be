    environment {
        AWS_REGION = "ap-southeast-1"
        AWS_ACCOUNT_ID = "682033501590"
        ECR_REPO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/maxweather"
        K8S_NAMESPACE = "default"
        K8S_DEPLOYMENT = "max_weather"
        IMAGE_TAG       = "latest-${env.BUILD_NUMBER}"
    }

pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-southeast-1'
        ECR_REPO = 'maxweather'
        EKS_CLUSTER = 'max_weather'
        BUILD_TAG = "build-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', credentialsId: 'git', url: 'git@github.com:haiktpm/max-weather-be.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t $ECR_REPO:$BUILD_TAG ."
                }
            }
        }

        stage('Authenticate with AWS ECR') {
            steps {
                script {
                    sh 'aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com'
                }
            }
        }

        stage('Tag & Push Image to ECR') {
            steps {
                script {
                    ACCOUNT_ID = sh(script: "aws sts get-caller-identity --query Account --output text", returnStdout: true).trim()
                    ECR_URI = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"

                    sh "docker tag $ECR_REPO:$BUILD_TAG $ECR_URI:$BUILD_TAG"
                    sh "docker push $ECR_URI:$BUILD_TAG"
                }
            }
        }

        stage('Update Kubernetes Deployment') {
            steps {
                script {
                    sh "aws eks update-kubeconfig --name $EKS_CLUSTER --region $AWS_REGION"

                    // Replace image in the deployment YAML dynamically
                    sh """
                    sed -i 's|<IMAGE_URI>|$ECR_URI:$BUILD_TAG|g' deployment/deployment.yaml
                    kubectl apply -f deployment/deployment.yaml
                    kubectl apply -f deployment/ingress.yaml
                    kubectl apply -f deployment/service.yaml
                    """
                }
            }
        }
    }
}
