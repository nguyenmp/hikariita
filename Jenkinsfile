pipeline {
    agent {
        docker {
            image 'python:3'

            // This is needed because multi-branch pipelines configure
            // a special user and workspace per change, and those users
            // cannot configure a python virtualenv
            args '-u root --privileged'
        }
    }
    stages {
        stage('Unit Tests') {
            steps {
                sh 'make test'
            }
            post {
                always {
                    junit 'test_results.xml'
                }
            }
        }
    }
}