import java.time.LocalDateTime
import hudson.model.*
import jenkins.model.*
import hudson.tasks.test.AbstractTestResultAction

pipeline {
    agent none
    stages {
        // stage of 
		
        stage('Regression Test') {
            steps {
                script {
				    echo "Run NRaaS Regression Test..."
					try {
						build job: 'Regression Test NRaaS', parameters: [
							string(name: 'product_name', value: 'NRaaS'),
							string(name: 'test_driver', value: params.test_driver),
							string(name: 'build_name', value: params.build_name),
							string(name: 'cluster_vm', value: 'mtl-nraas-vm20'),
							string(name: 'build_repo', value: params.build_repo),
							string(name: 'testset_repo', value: params.testset_repo),
							string(name: 'email_addr', value: params.email_addr),
							booleanParam(name: 'update_test_set', value: params.update_test_set),
							booleanParam(name: 'smoke', value: false),
							booleanParam(name: 'send_email', value: false),
							booleanParam(name: 'call_logging', value: params.call_logging),
							booleanParam(name: 'first_time_setup', value: params.first_time_setup),
							booleanParam(name: 'large_scale_cleanup', value: params.large_scale_cleanup),
							booleanParam(name: 'reserve_logs', value: params.reserve_logs),
							booleanParam(name: 'test_outside_cluster', value: params.test_outside_cluster)
						]  
					} catch(Exception e) {
						error 'Regression Test NRaaS stage has failed'
						throw e
					}
                }
            }
        }
        
        stage('Collect Results') {
			steps {
                script {
					echo "Collect Results NRaaS Regression Test..."
					try {
						build job: 'Collect Results NRaaS', parameters: [
						    string(name: 'test_driver', value: params.test_driver),
							string(name: 'build_name', value: params.build_name),
							booleanParam(name: 'send_email', value: params.send_email),
							string(name: 'email_addr', value: params.email_addr),
							string(name: 'product_name', value: params.product_name)
						]  
					}
					catch(Exception e) {
						error 'Regression Test NRC stage has failed'
						throw e
					}
				}
            }
        }
    }
	post {
	    failure {
	        emailext attachLog: true, from: 'Jenkins', body: 'NRaaS Run All Stages Test pipeline has failed, check build at $BUILD_URL and attached log for more details', subject: '${build_name} NRaaS All Stages Pipeline Fail', to: params.email_addr
	    }
	}
}      