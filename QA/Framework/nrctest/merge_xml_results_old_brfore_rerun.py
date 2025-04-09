#!/usr/bin/env python
#Merge NLPS-NRM regression test xml test result (Junit format) from different test classes XML files into one testsuite xml report file

import os
import sys
import xml.etree.ElementTree as ET

from os import listdir
from os.path import isfile, join

"""
Updated this script to merge test result from multiple test class Junit format xml files into one result report xml file   
Run this script on test driver under folder: \..\Framework\nrctest; 
Test result xml files & logs (directories) under:  \..\Framework\nrctest\log
The final merged regression test Junit format one xml result file: \..\Framework\nrctest; 
example usage:
    $ python merge_xml_results.py results1.xml results2.xml > results.xml
"""

# main
def main():
    #read args
    args = sys.argv[1:]

    #check if input with args
    if not args:
        #get a list of result files only (xml), not include sub-directories (log)
        xml_files_list = [f for f in listdir("./log") if isfile(join("./log", f))]
        xml_files2 = './log/'+ ' ./log/'.join(xml_files_list)
        xml_files_list2 = list(xml_files2.split(" "))
        #print 'xml_files2 content: %s' % xml_files_list2  # for debug
        merge_results(xml_files_list2)

    if '-h' in args or '--help' in args:
        usage()
        sys.exit(2)

    if args:
        # print 'args string: %s' % args[:] # for debug
        merge_results(args[:])

    # exit main
    exit(0)

# merge xml result function
def merge_results(xml_files):
    failures = 0
    tests = 0
    errors = 0
    time = 0.0
    cases = []

    #print 'xml file list: %s' % xml_files # for debug

    for file_name in xml_files:
        tree = ET.parse(file_name)
        test_suite = tree.getroot()
        failures += int(test_suite.attrib['failures'])
        tests += int(test_suite.attrib['tests'])
        errors += int(test_suite.attrib['errors'])
        time += float(test_suite.attrib['time'])
        cases.append(test_suite.getchildren())

    new_root = ET.Element('testsuite')
    new_root.attrib['failures'] = '%s' % failures
    new_root.attrib['tests'] = '%s' % tests
    new_root.attrib['errors'] = '%s' % errors
    new_root.attrib['time'] = '%s' % time
    for case in cases:
        new_root.extend(case)
    new_tree = ET.ElementTree(new_root)
    ET.dump(new_tree)

# command line usage printout
def usage():
    this_file = os.path.basename(__file__)
    #print 'Usage:  %s results1.xml results2.xml' % this_file # python2
    print('Usage:  %s results1.xml results2.xml' % this_file)   # Python3


if __name__ == '__main__':
    main()