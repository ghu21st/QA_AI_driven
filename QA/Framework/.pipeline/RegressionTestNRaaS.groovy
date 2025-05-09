import java.time.LocalDateTime

pipeline {
    agent { 
        label params.test_driver
    }
    stages {
        stage('First time setup NRC/NRaaS test set'){
            when {
                expression {
                    params.first_time_setup && params.test_outside_cluster
                }
            }
            agent {
                label params.test_driver
            }
            steps {
                script {
                    try {
                        // Clone remote repo under /opt/git_dev
                        sh '''
                        mkdir /opt/git_dev/
                        cd /opt/git_dev/
                        git init
                        git remote add origin git@git.labs.nuance.com:${testset_repo}
                        git config core.longpaths true
                        git config core.sparseCheckout true
                        echo NRC_test_automation/*>> .git/info/sparse-checkout
                        echo master/NRC_test_automation/*>> .git/info/sparse-checkout
                        '''
                        
                        // Create swap space on the server to avoid "fatal: Out of memory, malloc failed" in git pull
                        // sh'''
                        // sudo fallocate -l 4G /swapfile
                        // sudo chmod 600 /swapfile
                        // sudo mkswap /swapfile
                        // git pull --depth=1 origin master
                        // '''
                        
                        // Sync up branches from remote/origin/master and create local to track origin/NRC_Test_Automation_Branch
                        sh '''
                        git fetch
                        git branch nrc_test_automation_branch_local origin/NRC_Test_Automation_Branch
                        git checkout nrc_test_automation_branch_local
                        git merge origin/NRC_Test_Automation_Branch
                        '''
                    }
                    catch(Exception e) {
                        error 'Unable to setup NRC test set'
						throw e
                    }  
                }
            }
        }

        stage('Update NRC/NRaaS test set'){
            when {
                expression { 
					params.update_test_set
				}
            }
            agent { 
                label params.test_driver
            }
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
            steps {
                script{
                    sh '''echo "Updating ${product_name} test set via git..."'''
                    
                    if (params.test_outside_cluster) {
                        try {
                            // Pull new commits to /opt/git_dev
                            sh '''
                               cd /opt/git_dev/
                               git fetch
                               git reset --hard origin/master
                            '''
                            
                            // Overwrite local test set and test harness with new pulled from remote repository
                            sh '''
                               echo "Backup regression test results"
                               cp -r /package/unarchive/Framework/nrc_reg_results/ /root/
                               echo "Overwrite local test set & harness with update from remote repository..."
							rm -rf /package/unarchive/Framework
                               cp -r /opt/git_dev/NRC_test_automation/Framework /package/unarchive/
							cp /opt/jenkins/shell/*4jen.sh /package/unarchive/Framework
                               rm -rf /package/unarchive/Framework/nrc_reg_results/
                               mv /root/nrc_reg_results/ /package/unarchive/Framework/
                            '''
                          
                        }
                        catch(Exception e) {
                            error 'Unable to update NRC test set'
							throw e
                        }
                    } else {
                        error 'Test inside cluster not implemented'
                    }
                }
            }
        }

        stage('Backup previous test run logs & clean up'){
            agent { 
                label params.test_driver
            }
			environment {
				product=params.product_name.toLowerCase()
			}
            steps {
                script{
                    /* Change build display name to show NR build version */
                    def dt = LocalDateTime.now()
                    currentBuild.displayName = "${product_name}_${build_name}_${dt}_#${BUILD_NUMBER}"
                    if(params.smoke) {
						echo "For smoke test, ignore backup logs"
					} else {
						if (params.test_outside_cluster) {
							if (params.large_scale_cleanup) {
								try {
									sh '''
									cd /package/unarchive/Framework/
									echo "Delete all logs"
									rm -rf ./nrctest/log/*
									rm -rf ./nrctest/log_bak/*
									echo "Delete all xml results"
									rm -rf *.xml
									rm -rf nrc_reg_results/*
									echo "Delete previously reserved results and logs directories"
									rm -rf results-nrc-*
									'''
								}
								catch(Exception e) {
									error 'Unable to perform large-scale clean up'
									throw e
								}
							} else {
								try {
									sh '''
									echo "Move previous test logs to backup folder /package/unarchive/Framework/nrctest/log_bak..."
									cd /package/unarchive/Framework/nrctest/
									rm -rf ./log_bak/*
									mkdir -p ./log_bak
									[ ! "$(ls -A ./log/)" ] || mv ./log/* ./log_bak/
									''' // move files if non-empty directory
									
									sh '''
									echo "Move previous ${product_name} regression test results to backup folder /package/unarchive/Framework/nrc_reg_results..."
									cd /package/unarchive/Framework/
									mkdir -p ./${product}_reg_results
									[ ! -f ${product}_reg_result_* ] || mv ${product}_reg_result_* ./${product}_reg_results/
									''' 
								}
								catch(Exception e) {
									error 'Unable to clean up previous test logs'
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

        stage('Run Test'){
            agent { 
                label params.test_driver
            }
			environment {
				product=params.product_name.toLowerCase()
			}
            steps {
                script {
                    if (params.test_outside_cluster) {
                        if (params.product_name == 'NRaaS'){
						    if(params.smoke) {
                                echo "Running NRaaS smoke test..."
								sh '''
								python3 /opt/jenkins/py/setTestCfg.py ${product_name}
								'''
                                try { 
                                    if (params.call_logging) {
                                        sh '''
										cd /package/unarchive/Framework
 										./nrctest.sh RegressionTestNRaaS/gRPCTest/ test_03_grammar.NRCTestGrammar.test004_UriGrammarYes -clog
                                        '''
                                    } else {
                                        sh '''
										cd /package/unarchive/Framework
										./nrctest.sh RegressionTestNRaaS/gRPCTest/ test_03_grammar.NRCTestGrammar.test004_UriGrammarYes
                                        '''
                                    }
                                } catch (Exception e) {
                                    error '''Smoke test failed, verify NRaaS build and check logs'''
									throw e
                                }  
                            } else {
                                echo "Running NRaaS regression test on CD4 ..."
								sh '''
								cd /package/unarchive/Framework
								if [ "$(ls -A nrctest/log)" ]; then
									cp -r ./nrctest/log/* ./nrctest/log_bak
									rm -fr ./nrctest/log/*
								fi
								'''								
                                try {
                                    sh '''
                                        cd /package/unarchive/Framework
                                        sh regression_nraas_test4jen.sh
                                        '''

                                    // Rename .xml result file to include build name
									echo "rename .xml regression results to add build ${build_name}"
                                    sh '''
									cd /package/unarchive/Framework
									reg_result=$(ls ${product}_reg_result_2*.xml)
									if [ -f ${reg_result} ]; then
										reg_result4jen=$(echo ${reg_result} | sed -e "s/reg_result/reg_result_${build_name}/")
										mv ${reg_result} ${reg_result4jen}
									else
									    echo "ERROR: Cannot find regression result file"
										exit 1
									fi
                                    '''
                                
                                    if (params.reserve_logs) {
                                        sh '''
                                        cd /package/unarchive/Framework
                                        mkdir -p results-nraas-${build_name}
                                        echo yes | cp ${product}_*.xml ./results-nraas-${build_name}
                                        mv ./nrctest/log/* ./results-nraas-${build_name}
                                        '''
                                    }
                                
                                } catch (Exception e) {
                                    error '''Regression test failed, verify NRaaS build and check logs'''
									throw e
                                }  
							}
						} else {
							sh '''
							python3 /opt/jenkins/py/setTestCfg.py ${product_name} NRCServiceIP=${cluster_vm}
							'''              
                            if(params.smoke) {
								echo "Running NRC smoke test..."
                                try { 
                                    if (params.call_logging) {
                                        sh '''
                                            cd /package/unarchive/Framework
                                            ./nrctest.sh RegressionTest/gRPCTest/ test_03_grammar.NRCTestGrammar.test004_UriGrammarYes -clog
                                            '''
                                    } else {
                                        sh '''
                                            cd /package/unarchive/Framework
                                            ./nrctest.sh RegressionTest/gRPCTest/ test_03_grammar.NRCTestGrammar.test004_UriGrammarYes
                                            '''
                                    }
                                } catch (Exception e) {
                                    error '''Smoke test failed, verify NRC build and check logs'''
									throw e
                                }  
                            } else {
                                echo "Running NRC regression test..."
								sh '''
								cd /package/unarchive/Framework
								if [ "$(ls -A nrctest/log)" ]; then
									cp -r ./nrctest/log/* ./nrctest/log_bak
									rm -fr ./nrctest/log/*
								fi
								'''
                                try {
                                    if (params.call_logging) {
                                        sh '''
                                        cd /package/unarchive/Framework
                                        sh regression_nrc_test_with_callLog4jen.sh
                                        '''
                                    } else {
                                        sh '''
                                        cd /package/unarchive/Framework
                                        sh regression_nrc_test4jen.sh
                                        '''
                                    }
                                
                                    // Rename .xml result file to include build name
				                    echo "rename .xml regression results to add build ${build_name}"
				                    sh '''
                                    cd /package/unarchive/Framework
									reg_result=$(ls ${product}_reg_result_2*.xml)
									if [ -f ${reg_result} ]; then
										reg_result4jen=$(echo ${reg_result} | sed -e "s/reg_result/reg_result_${build_name}/")
										mv ${reg_result} ${reg_result4jen}
									else
									    echo "ERROR: Cannot find regression result file"
										exit 1
									fi
                                    '''
                                    if (params.reserve_logs) {
                                        sh '''
                                        cd /package/unarchive/Framework
                                        mkdir -p results-nrc-${build_name}
                                        echo yes | cp ${product}_reg_result_*.xml ./results-nrc-${build_name}
                                        mv ./nrctest/log/* ./results-nrc-${build_name}
                                        '''
                                    }
                                } catch (Exception e) {
                                    error '''Regression test failed, verify NRC build and check logs'''
									throw e
                                }  
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
    		    if(params.send_email) {
				    if(params.smoke) {
					    emailext attachLog: true, from: 'Jenkins', body: 'Test pipeline has failed in the ${product_name} Regression Test stage, check attached logs for more details.', subject: '${product_name} Smoke Test Fail', to: '${email_addr}'
					} else {
						emailext attachLog: true, from: 'Jenkins', body: 'Test pipeline has failed in the ${product_name} Regression Test stage, check attached logs for more details.', subject: '${product_name} Test Fail', to: '${email_addr}'
					}
				}
		    }
		}
		success {
		    script {
    		    if(params.send_email) {
				    if(params.smoke) {
						emailext attachLog: true, from: 'Jenkins', body: 'Test pipeline for ${product_name} Regression Test passed successfully, check attached logs for more details.', subject: '${product_name} Smoke Test Pass', to: '${email_addr}'
					} else {
						emailext attachLog: true, from: 'Jenkins', body: 'Test pipeline for ${product_name} Regression Test passed successfully, check attached logs for more details.', subject: '${product_name} Test Pass', to: '${email_addr}'
					}
				}
		    }
		}
	}
}
