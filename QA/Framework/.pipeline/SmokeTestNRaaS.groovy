import java.time.LocalDateTime

test_result = ""

pipeline {
    agent { 
        label params.test_driver
    }
    stages {
        stage('Run Smoke Test'){
            agent { 
                label params.test_driver
            }
            steps {
                script {
                    if (params.test_outside_cluster) {
                        if (params.product_name == 'NRaaS'){
						    echo "Running NRaaS smoke test..."
							sh '''
								python3 /opt/jenkins/py/setTestCfg.py ${product_name}
							'''
                            try { 
                                sh '''
										cd /package/unarchive/Framework
										while IFS= read -r test; do
										    [[ $test =~ ^#.* ]] && continue
											./nrctest.sh RegressionTestNRaaS/gRPCTest/ ${test}
										done <<< "${smoke_tests}"		
                                    '''
							} catch (Exception e) {
                                error '''NRaaS Smoke test failed, verify NRaaS build and check logs'''
							    throw e
                            }  
                        } else {
						    echo "Running NRC smoke test..."
							sh '''
							python3 /opt/jenkins/py/setTestCfg.py ${product_name} NRCServiceIP=${cluster_vm}
							'''              
                            try { 
                                if (params.call_logging) {
                                    sh '''
                                        cd /package/unarchive/Framework
 										while IFS= read -r test; do
										    [[ $test =~ ^test_01.* ]] && continue
											[[ $test =~ ^#.* ]] && continue
											./nrctest.sh RegressionTest/gRPCTest/ ${test} -clog
										done <<< "${smoke_tests}"
                                        '''
                                } else {
								    sh '''
										cd /package/unarchive/Framework
										while IFS= read -r test; do
											[[ $test =~ ^#.* ]] && continue
											./nrctest.sh RegressionTest/gRPCTest/ ${test}
										done <<< "${smoke_tests}"
									'''
								}
                            } catch (Exception e) {
                                error '''NRC Smoke test failed, verify NRC build and check logs'''
								throw e
                            }  
						}
                    } else {
                        error 'Test inside cluster not implemented'
                    }
                }
            }
        }
    }
	post {
	    failure {
			script {
			    sh 'sleep 5'
				test_result = sh (
					script: "python3 /opt/jenkins/py/sumSmoke.py ${BUILD_NUMBER}",
					returnStdout: true
				).trim()		
    		    if(params.send_email) {
				    if(params.call_logging) {
					if (params.product_name == "NRaaS") {
							emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test enabled call logging failed. Below tests are triggered to run:\n\n${test_result}", subject: '${product_name} Smoke Test (call logging) Fail', to: '${email_addr}'
						} else {
						    emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test enabled call logging failed. The build is ${build_name} installed on ${cluster_vm}. Below tests are triggered to run:\n\n${test_result}", subject: '${product_name} Smoke Test (call logging) Fail', to: '${email_addr}'
						}
					} else {
					    if (params.product_name == "NRaaS") {
							emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test failed. Below tests are run:\n\n${test_result}", subject: '${product_name} Smoke Test Fail', to: '${email_addr}'
						} else {
						    emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test failed. The build is ${build_name} installed on ${cluster_vm}. Below tests are run:\n\n${test_result}", subject: '${product_name} Smoke Test FAil', to: '${email_addr}'
						}
					}
				}
		    }
		}
		success {
		    script {
			    sh 'sleep 5'
				test_result = sh (
					script: "python3 /opt/jenkins/py/sumSmoke.py ${BUILD_NUMBER}",
					returnStdout: true
				).trim()					
    		    if(params.send_email) {
				    if(params.call_logging) {
						if (params.product_name == "NRaaS") {
							emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test enabled call logging passed successfully. Below tests are tested:\n\n${test_result}", subject: '${product_name} Smoke Test (call logging) Pass', to: '${email_addr}'
						} else {
						    emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test enabled call logging passed successfully. The build is ${build_name} installed on ${cluster_vm}. Below tests are tested:\n\n${test_result}", subject: '${product_name} Smoke Test (call logging) Pass', to: '${email_addr}'
						}
					} else {
					    if (params.product_name == "NRaaS") {
							emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test passed successfully. Below tests are tested:\n\n${test_result}", subject: '${product_name} Smoke Test Pass', to: '${email_addr}'
						} else {
						    emailext attachLog: true, from: 'Jenkins', body: "${product_name} Smoke Test passed successfully. The build is ${build_name} installed on ${cluster_vm}. Below tests are tested:\n\n${test_result}", subject: '${product_name} Smoke Test Pass', to: '${email_addr}'
						}
					}
				}
		    }
		}
	}
}
