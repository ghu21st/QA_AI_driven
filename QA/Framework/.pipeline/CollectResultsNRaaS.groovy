import java.time.LocalDateTime
import hudson.model.*
import jenkins.model.*
import hudson.tasks.test.*

summary = ""

pipeline {
    agent { 
        label params.test_driver
    }
    stages {
        stage('Import & Report Results'){

            options {
				timeout(5)
			}
			post {
				cleanup {
					/* clean up our workspace */
					deleteDir()
					/* clean up tmp directory */
					dir("${workspace}@tmp") {
						deleteDir()
					}
					/* clean up script directory */
					dir("${workspace}@script") {
						deleteDir()
					}
				}				
			}
			environment {
                product=params.product_name.toLowerCase()
            }
            steps {
                script{
                    /* Change build display name to show NR build version */
                    def dt = LocalDateTime.now()
                    currentBuild.displayName = "${product_name}_${build_name}_${dt}_#${BUILD_NUMBER}"
					sh '''
                    cd /package/unarchive/Framework
					if [ ! -f ${product}_reg_result_${build_name}*.xml ]; then
						reg_result=$(ls ${product}_reg_result_2*.xml)
						if [ -f ${reg_result} ]; then
							reg_result4jen=$(echo ${reg_result} | sed -e "s/reg_result/reg_result_${build_name}/")
							mv ${reg_result} ${reg_result4jen}
						else
						    echo "ERROR: There is no ${product_name} regression result."
                            exit 1
                        fi
					fi
					'''
                    dir('/package/unarchive/Framework/'){
                        summary = sh (
                            script: "python3 /opt/jenkins/py/summaryGen.py ${product} ${build_name} ${product}_reg_result_${build_name}*.xml",
                            returnStdout: true
                        ).trim()
                    }
			    }
            }
        }
    }
	post {
	    failure {
		    script {
    		    if(params.send_email)
    			    emailext attachLog: true, from: 'Jenkins', body: 'Failed to Collect test results, check log for more details', subject: 'Result Collection ${build_name} Fail', to: '${email_addr}'
		    }
		}
		success {
		    script {
		        if (params.send_email)
		            emailext (
		                attachLog: true,
		                to: '${email_addr}',
		                from: 'Jenkins',
		                subject: 'Result Collection of ${build_name} Pass',
						mimeType: 'text/html',
		                body: summary
                    )
		    }
		}
		unstable {
		    script {
		        if (params.send_email)
		            emailext (
		                attachLog: true,
		                to: '${email_addr}',
		                from: 'Jenkins',
		                subject: 'Result Collection ${build_name} Unstable',
						mimeType: 'text/html',
		                body: summary
	                )
		    }
		}
	}
}
