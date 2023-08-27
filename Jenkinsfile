pipeline { 
    agent any  

        stages { 

            stage('Build Env File') {

                steps {

                    withCredentials([string(credentialsId: 'FAST_API_AUTH_SECRET', variable: 'AUTH_SECRET')]) {
                    withCredentials([string(credentialsId: 'ORIGINS_DOMAIN_SECRET', variable: 'ORIGINS_DOMAIN')]) {

                        withCredentials([usernamePassword(credentialsId: 'MYSQL_USER_PASS_2', passwordVariable: 'PASSWORD_1', usernameVariable: 'USERNAME_1')]) {

                            writeFile file: './.env', text: """
DB_USER="${USERNAME_1}" 
DB_PASSWORD="${PASSWORD_1}" 
DB_NAME="ezcampus_db"
DB_PORT="3306"
DB_HOST="mysql-instance"
DB_DIR="."
DEBUG=0
FASTAPI_HOST="0.0.0.0"
FASTAPI_PORT="8080"
AUTH_SECRET_KEY="${AUTH_SECRET}"
origins_domain="${ORIGINS_DOMAIN}"
"""
                        }
                        }
                    }
                }
            }

            stage('Build Docker Image') { 

                steps { 

                    sshPublisher(
                            failOnError: true,
                            publishers: [
                            sshPublisherDesc(
                                configName: '2GB_Glassfish_VPS',
                                transfers: [
                                sshTransfer(cleanRemote: true,
                                    excludes: '',
                                    execCommand: '''
                                    cd ~/pipeline_fastapi_backend
                                    chmod +x build.sh
                                    ./build.sh USE_LOG_FILE
                                    chmod +x deploy.sh
                                    ./deploy.sh USE_LOG_FILE
                                    rm -rf ./.env
                                    ''',
                                    execTimeout: 120000,
                                    flatten: false,
                                    makeEmptyDirs: true, 
                                    noDefaultExcludes: false,
                                    patternSeparator: '[, ]+',
                                    remoteDirectory: 'pipeline_fastapi_backend',
                                    remoteDirectorySDF: false, 
                                    removePrefix: '', 
                                    sourceFiles: 'Dockerfile, requirements.txt, build.sh, deploy.sh, .env, entrypoint.sh, **')
                                ], 
                            usePromotionTimestamp: false,
                            useWorkspaceInPromotion: false,
                            verbose: false)
                                ])
                }
            }
        }

    post {

        always {

            discordSend(
                    description: currentBuild.result, 
                    enableArtifactsList: false, 
                    footer: '', 
                    image: '', 
                    link: '', 
                    result: currentBuild.result, 
                    scmWebUrl: '', 
                    thumbnail: '', 
                    title: env.JOB_BASE_NAME, 
                    webhookURL: "${DISCORD_WEBHOOK_1}"
                    )
        }
    }
}

