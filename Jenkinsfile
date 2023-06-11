pipeline { 
    agent any  

    stages { 
        
        stage('Build Docker Image') { 
            steps { 

                    sshPublisher(publishers: [
                        sshPublisherDesc(configName: '2GB_Glassfish_VPS', transfers: [
                            sshTransfer(cleanRemote: true, excludes: '', execCommand: '''
                            chmod +x build.sh
                            ./build.sh
                            ''', execTimeout: 120000, flatten: false, makeEmptyDirs: true, 
                            noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: 'fastapi_backend', remoteDirectorySDF: false, 
                            removePrefix: '', sourceFiles: 'Dockerfile, requirements.txt, build.sh, .env, entrypoint.sh, fastapi_backend/**')
                        ], 
                        usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)
                    ])
            }
        }
    }
}

