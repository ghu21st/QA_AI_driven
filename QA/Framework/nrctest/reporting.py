#!/usr/bin/env python

import os
import sys
import xml.etree.ElementTree as ET
import datetime as dt
import re
import csv

from os import listdir
from os.path import isfile, join, isdir
from prettytable import PrettyTable, ALL

"""
This script prints a formatted test summary based on the test results
"""


TerminalColors = {
    'HEADER' : '\033[95m',
    'BLUE' : '\033[94m',
    'CYAN' : '\033[96m',
    'GREEN' : '\033[92m',
    'WARNING' : '\033[93m',
    'FAIL' : '\033[91m',
    'ENDC' : '\033[0m',
    'BOLD' : '\033[1m',
    'UNDERLINE' : '\033[4m'
}
    
test_type_str = ""

# main
def main():

    
    args = sys.argv[1:]
    os.environ['rerun_reports_dir'] = './log'
    
    if(len(args) > 4):
        print("Invalid Number of args!\n")
        usage()
        exit(-1)
        
    if('-csv' in args):
        os.environ['output_csv'] = 'True'
    if('-txt' in args):
        os.environ['output_txt'] = 'True'
    if('-dir' in args):
        index = args.index("-dir")
        if(not isdir(args[index + 1])):
            print("The directory passed is invalid! try again")
            exit(-1)
        os.environ['rerun_reports_dir'] = args[index + 1]
    
    
    # get a list of result files only (xml), not include sub-directories (log)
    xml_files_list = [f for f in listdir(os.environ.get('rerun_reports_dir')) if isfile(join(os.environ.get('rerun_reports_dir'), f))]

    # dictionary that holds groups of reports (Main and reruns)
    suites_dict = {}

    # a dictionary that holds the name of the suite as a key and a
    # dictionary of test case name => number of reruns as a value
    suites_tests = {}
    
    # similar to above but stores test result instead rerun count 
    suites_tests_result = {}
    

    # populating the dictionary
    for xml_report in xml_files_list:
        file_name = xml_report.split('-')[1]
        if suites_dict.get(file_name) != None:
            suites_dict[file_name].append(xml_report)
        else:
            suites_dict[file_name] = [xml_report]

    for key, val in suites_dict.items():
        suites_tests_result[key], suites_tests[key] = get_suite_summary(val)

    # a list containing the rows of detailed report as lists (each list is a row)
    test_details = []

    # tables for summary and detailed report
    detailed_table = PrettyTable()
    summary_table = PrettyTable()

    detailed_table.field_names = ["Test Suite Name", "Test Case Name", " Total Reruns", "Result (pass/fail)"]
    detailed_table.title = TerminalColors['BOLD'] + 'Test Details' + TerminalColors['ENDC']
    

    for suite_name, tests_dict in suites_tests.items():
        for case_name, case_rerun in tests_dict.items():
            test_details.append(list([suite_name.split('.')[0], case_name, case_rerun, suites_tests_result[suite_name][case_name]]))
    
    if(bool(os.environ.get('output_csv'))):
        data = ["TestSuiteName", "TestCaseName", "TotalReruns", "Result(pass/fail)"]
        timestamp = str(dt.datetime.now()).split('.')[0].replace(' ', '-')
        with open(f'../test_cases_details_{timestamp}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([data])
            writer.writerows(test_details)
        
    summary_list = []
        
    if(len(suites_tests.keys()) == len(xml_files_list)):
        summary_list = list(filter(lambda row: row[3] == 'Failure' or row[3] == 'Error', test_details))
    else:
        summary_list = list(filter(lambda row: row[2] > 0, test_details))
    
    
    summary = {}
    # summary['test_type'] = 'NRaaS' if context.config.get('NRCServiceURL') != None else 'NRC'
    summary['test_type'] = test_type_str.split(' ')[0]
    # summary['host_url'] = context.config.get('NRCServiceIP') if summary['test_type'] == 'NRC' else context.config['NRCServiceURL']
    summary['host_url'] = test_type_str.split(' ')[-1]
    summary['host_url'] = "Server Host URL/IP: " + summary['host_url']
    summary['end_statement'] = f"\n\n{summary['test_type']} Test Completed - Check the details below"
    
    
    summary['tests_total_number'] = len(test_details)
    summary['total_number_suites'] = len(suites_dict.keys())
    summary['failed_tests_num'] = len(list(filter(lambda test: test[3] == 'Failure', test_details)))
    summary['error_tests_num'] = len(list(filter(lambda test: test[3] == 'Error', test_details)))
    summary['passed_tests_num'] = summary['tests_total_number'] - summary['failed_tests_num'] - summary['error_tests_num']
        
    if(bool(os.environ.get('output_txt'))):
        output_results_to_txt(summary_list, summary)
    
     
    summary_list = map(lambda row: [row[0], truncate_long_name(row[1]), row[2], colorize_text(row[3])], summary_list)
    detailed_table.add_rows(summary_list)
    detailed_table.align = "l"
    detailed_table.border = True
    detailed_table.hrules = ALL

    summary_table.add_rows([[TerminalColors['BOLD'] + 'Number Of Test Suites: ', TerminalColors['UNDERLINE'] + str(summary['total_number_suites']) + TerminalColors['ENDC']],
                            [TerminalColors['BOLD'] + 'Total Number Of Tests', TerminalColors['UNDERLINE'] + str(summary['tests_total_number']) + TerminalColors['ENDC']], 
                            [TerminalColors['BOLD'] + 'Passed Tests Number', TerminalColors['GREEN'] + str(summary['passed_tests_num']) + TerminalColors['ENDC']],
                            [TerminalColors['BOLD'] + 'Failed Cases Number', TerminalColors['FAIL'] + str(summary['failed_tests_num']) + TerminalColors['ENDC']],
                            [TerminalColors['BOLD'] + 'Error Cases Number', TerminalColors['WARNING'] + str(summary['error_tests_num']) + TerminalColors['ENDC']]])
    summary_table.align = "l"
    summary_table.header = False
    summary_table.title = TerminalColors['BOLD'] + 'Test Summary' + TerminalColors['ENDC']
    

    print(TerminalColors['BOLD'] + summary['end_statement'] + TerminalColors['ENDC'])
    print(TerminalColors['BOLD'] + summary['host_url'] + '\n\n' + TerminalColors['ENDC'])
    print(summary_table)
    print("\n\n")
    print(detailed_table)
    # exit main
    exit(0)


# Truncate long test case name to fit in a formatted table
def truncate_long_name(name):
    length = len(name)
    if (length > 75):
        return name[:70] + "...."
    else:
        return name


def colorize_text(text):
    if(text == 'Pass'):
        return TerminalColors['GREEN'] + text + TerminalColors['ENDC']
    elif(text == 'Failure'):
        return TerminalColors['FAIL'] + text + TerminalColors['ENDC']
    else:
        return TerminalColors['WARNING'] + text + TerminalColors['ENDC']


def output_results_to_txt(test_details_summary, report_summary):
    # create the two tables
    cases_details_table = PrettyTable()
    report_summary_table = PrettyTable()
    
    test_details_summary = map(lambda row: [row[0], truncate_long_name(row[1]), row[2], row[3]], test_details_summary)
    
    
    # add the required rows to the report summary
    report_summary_table.add_rows([['Number Of Test Suites: ', str(report_summary['total_number_suites'])],
                            ['Total Number Of Tests', str(report_summary['tests_total_number'])], 
                            ['Passed Tests Number', str(report_summary['passed_tests_num'])],
                            ['Failed Cases Number', str(report_summary['failed_tests_num'])],
                            ['Error Cases Number', str(report_summary['error_tests_num'])]])
    report_summary_table.align = "l"
    report_summary_table.header = False
    report_summary_table.title = 'Test Summary'
    
    # add the rows for test details table
    cases_details_table.add_rows(test_details_summary)
    cases_details_table.align = "l"
    cases_details_table.border = True
    cases_details_table.hrules = ALL
    cases_details_table.title = 'Test Details'
    cases_details_table.field_names = ["Test Suite Name", "Test Case Name", " Total Reruns", "Result (pass/fail)"]
    
    # write to a file
    timestamp = str(dt.datetime.now()).split('.')[0].replace(' ', '-')
    with open(f'../test_report_{timestamp}.txt', 'w') as w:
        w.write(report_summary['end_statement'])
        w.write('\n\n')
        w.write(report_summary['host_url'])
        w.write('\n\n')
        w.write(str(report_summary_table))
        w.write('\n\n')
        w.write(str(cases_details_table))
        
def usage():
    print("This script is used to print test result summary and output the test cases status")
    print("if ran without any args it will default to ./log directory in the test framework to get the test reports")
    print("custom usage:\n -csv\t\t\t output all test cases names/suites and status (pass/fail/error) to an csv file\n -dir <custom dir>\t instruct the script to look for the test reports in a different directory")
        

# extract the server IP/Hostname/URL where the test was run
def record_server_info(report_tree):
        global test_type_str
        sys_out_tags = report_tree.findall('testcase/system-out')
        test_log = sys_out_tags[0].text
        for line in test_log.split('\n'):
            if 'NRC gRPC test server URL is' in line:
                test_type_str = line
            elif 'NRaaS secure URL is' in line:
                test_type_str = line
        
def get_suite_summary(rerun_list):
    '''
    This method takes a list of xml report group (main and reruns for a test suite)
    and returns a dictionary with test case names as the key and the number of reruns 
    before a test passes (if it passes) as a value. 
    '''

    # get the main run from the list and create ElementTree
    pattern = re.compile(".*__MAIN.xml")
    connection_pattern = re.compile("TEST-test_01_connection*")
    
    main_report = list(
        filter(lambda item: pattern.match(item) != None, rerun_list))[0]
    main_report_path = os.environ.get('rerun_reports_dir') + '/' + main_report
    main_tree = ET.parse(main_report_path)
    if(connection_pattern.match(main_report) != None):
        record_server_info(main_tree)
    
    # a dictionary of case => number of reruns (key => val)
    # 0 would indicate passing first time (no rerun)
    # if number of reruns equals max reruns set it means the
    # test case still failed after going through all reruns set
    # in the framework
    test_cases = {}
    
    
    # similar to above but stores the test result as a value
    # test name => test result
    test_result = {}
    

    # list of all test cases in the main run
    main_run_test_cases = main_tree.findall('testcase')
    

    # initialize all test cases to 0
    for case in main_run_test_cases:
        test_cases[case.attrib.get('name')] = 0
        test_result[case.attrib.get('name')] = 'Pass'

    index_track = 0
    
    for report in rerun_list:
        index_track += 1
        current_tree = ET.parse(os.environ.get('rerun_reports_dir') +"/{}".format(report))
        failed = current_tree.findall('testcase/failure/..')
        errors = current_tree.findall('testcase/error/..')

        failed_cases_name_list = [el.attrib.get('name') for el in failed]
        error_cases_name_list = [el.attrib.get('name') for el in errors]


        if(len(rerun_list) == 1):
            # in this case there is no re-run
            for name in error_cases_name_list:
                test_result[name] = 'Error'
            for name in failed_cases_name_list:
                test_result[name] = 'Failure'
        elif(index_track != len(rerun_list)):
            # increment rerun number for each failing/error case
            for name in error_cases_name_list:
                test_cases[name] += 1
            for name in failed_cases_name_list:
                test_cases[name] += 1
        else:
            # if this is the last rerun report, see what is still
            # failing/error and update the merged report accordingly
            if(index_track == len(rerun_list)):
                for name in error_cases_name_list:
                    test_result[name] = 'Error'
                for name in failed_cases_name_list:
                    test_result[name] = 'Failure'
    return [test_result, test_cases]


if __name__ == '__main__':
    main()
