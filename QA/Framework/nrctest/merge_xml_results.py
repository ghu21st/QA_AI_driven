#!/usr/bin/env python
#Merge NLPS-NRM regression test xml test result (Junit format) from different test classes XML files into one testsuite xml report file

import os
import sys
import xml.etree.ElementTree as ET
import time as t
import re
import copy

from os import listdir
from os.path import isfile, join

"""
UPDATE 02/21/2023:
Updated this script to produce one report for test result including the result 
of reruns for failed cases. These changes have been made to accommodate the new
changes in nrctest.py where failed test cases rerun automatically 

Updated this script to merge test result from multiple test class Junit format xml files into one result report xml file   
Run this script on test driver under folder: \..\Framework\nrctest; 
Test result xml files & logs (directories) under:  \..\Framework\nrctest\log
The final merged regression test Junit format one xml result file: \..\Framework\nrctest; 
example usage:
    $ python merge_xml_results.py results1.xml results2.xml
"""

# main
def main():
    #read args
    args = sys.argv[1:]

    #check if input with args
    if not args:
        #get a list of result files only (xml), not include sub-directories (log)
        xml_files_list = [f for f in listdir("./log") if isfile(join("./log", f))]
        
        # dictionary that holds groups of reports (Main and reruns) 
        suites_dict = {}
        # this holds a list of ET object for the test suits processed after rerun (updated success cases)
        tree_objects = []
        
        # populating the dictionary
        for xml_report in xml_files_list:
            file_name = xml_report.split('-')[1]
            if suites_dict.get(file_name) != None:
                suites_dict[file_name].append(xml_report)
            else:
                suites_dict[file_name] = [xml_report]
            
        for val in suites_dict.values():
            result = merge_reruns(val)
            tree_objects.append(result)
        merge_results(tree_objects)               

    if '-h' in args or '--help' in args:
        usage()
        sys.exit(2)

    if args:
        # print 'args string: %s' % args[:] # for debug
        merge_results(args[:]) 

    # exit main
    exit(0)


def update_elements_map(tree):
    elements_map = {}
    for item in tree.iter():
        if(item.tag == 'testcase'):
            elements_map[item.attrib.get("name")] = item
    return elements_map            


def merge_reruns(rerun_list):
    # get the main run from the list and create ElementTree
    pattern = re.compile(".*__MAIN.xml")
    main_report = list(filter(lambda item: pattern.match(item) != None, rerun_list))[0]
    main_report_path = './log/' + main_report
    main_tree = ET.parse(main_report_path)
    
    
    # get the parent map for main report
    elements_map = update_elements_map(main_tree)
    # number of failed cases in the main report
    failed_num = int(main_tree.getroot().attrib.get('failures'))
    error_num = int(main_tree.getroot().attrib.get('errors'))
    total_main_issues = failed_num + error_num

    for report in rerun_list:
        # ignore if the report is main
        if(report == main_report):
            continue
        # create an ET from the rerun report
        current_tree = ET.parse("./log/{}".format(report))

        cases_list = current_tree.findall('testcase')
        for case in cases_list:
            case_name = case.attrib.get("name")
            case_copy = copy.deepcopy(case)
            main_tree.getroot().remove(elements_map[case_name])
            main_tree.getroot().append(case_copy)
            elements_map = update_elements_map(main_tree)
            
    main_tree.getroot().attrib['errors'] = str(len(main_tree.findall('testcase/error')))
    main_tree.getroot().attrib['failures'] = str(len(main_tree.findall('testcase/failure')))
    return main_tree
    
    


# merge xml result function
def merge_results(xml_tree_list):
    failures = 0
    tests = 0
    errors = 0
    time = 0.0
    cases = []

    #print 'xml file list: %s' % xml_files # for debug

    for tree in xml_tree_list:
        test_suite = tree.getroot()
        failures += int(test_suite.attrib['failures'])
        tests += int(test_suite.attrib['tests'])
        errors += int(test_suite.attrib['errors'])
        time += float(test_suite.attrib['time'])
        cases.append(list(test_suite))

    new_root = ET.Element('testsuite')
    new_root.attrib['failures'] = '%s' % failures
    new_root.attrib['tests'] = '%s' % tests
    new_root.attrib['errors'] = '%s' % errors
    new_root.attrib['time'] = '%s' % time
    for case in cases:
        new_root.extend(case)
    new_tree = ET.ElementTree(new_root)

    # opening a file to write the xml report
    output_xml_name = "../nrc_reg_result_{}.xml".format(t.strftime("%Y%m%d%H%M%S"))
    f = open(output_xml_name, "ab")
    ET.ElementTree.write(self=new_tree,file_or_filename=f,encoding='UTF-8')
    f.close()
    
    # This should be for debug only
    # ET.dump(new_tree)
    

# command line usage printout
def usage():
    this_file = os.path.basename(__file__)
    #print 'Usage:  %s results1.xml results2.xml' % this_file # python2
    print('Usage:  %s results1.xml results2.xml' % this_file)   # Python3


if __name__ == '__main__':
    main()