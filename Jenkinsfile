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
                            cd ~/pipline_fastapi_backend
                            chmod +x build.sh
                            ./build.sh
                            ''', execTimeout: 120000, flatten: false, makeEmptyDirs: true, 
                            noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'pipline_fastapi_backend', remoteDirectorySDF: false, 
                            removePrefix: '', sourceFiles: 'Dockerfile, requirements.txt, build.sh, .env, entrypoint.sh, **')
                        ], 
                        usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)
                    ])
            }
        }
    }
}

