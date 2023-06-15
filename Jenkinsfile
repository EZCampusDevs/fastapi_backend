pipeline { 
    agent any  

    stages { 
        
        stage('Build Docker Image') { 
            steps { 

                    sshPublisher(
                        failOnError: true,
                        publishers: [
                        sshPublisherDesc(configName: '2GB_Glassfish_VPS', transfers: [
                            sshTransfer(cleanRemote: true, excludes: '', execCommand: '''
                            cd ~/pipeline_fastapi_backend
                            chmod +x build.sh
                            ./build.sh
                            chmod +x deploy.sh
                            ./deploy.sh
                            ''', execTimeout: 120000, flatten: false, makeEmptyDirs: true, 
                            noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'pipeline_fastapi_backend', remoteDirectorySDF: false, 
                            removePrefix: '', sourceFiles: 'Dockerfile, requirements.txt, build.sh, deploy.sh, .env, entrypoint.sh, **')
                        ], 
                        usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)
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

