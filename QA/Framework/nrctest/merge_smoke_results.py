import glob
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import os

passed = 0
failed = 0
errors = 0
count = 0

def parse_file(file_path: str, word_to_find: str):
    if not isinstance(file_path, str):
        raise Exception("'file_path' should be string.")

    if not isinstance(word_to_find, str):
        raise Exception("'word_to_find' should be string.")

    with open(file_path, 'r') as file1:
        lines = file1.readlines()

    matched_lines = []
    for line in lines:
        if line.find(word_to_find) != -1:
            matched_lines.append(line)

    return matched_lines


    global passed,failed, errors, count
    files = glob.glob('/QA/NRC_Test/Framework/nrctest/log/**/*.log', recursive = True)
    files.sort()
    count=len(files)
    loggedFiles='Total test results is:',count
    print(loggedFiles)
    for file in files:
        print(file)
        matches = parse_file(file, 'Assert recognition validation...')
        for item in matches:
            print(item)
        if not any("Assert recognition validation" in item for item in matches):
            print("Error")
            errors +=1
        elif any ("Assert recognition validation... Failed!" in item for item in matches):
            print("Fail")
            failed += 1
        else:
            print("Pass")
            passed += 1
    print("Error cases count is",errors)
    print("Passed cases count is",passed)
    print("Failed cases count is",failed)

def create_report():
    global passed,failed, errors, count
    files = glob.glob(os.environ.get('TESTPATH')+'/ev2/Scripts/Framework/nrctest/log/**/*.log', recursive = True)
    files.sort()
    count=len(files)
    loggedFiles='Total test results is:',count
    print(loggedFiles)
    for file in files:
        print(file)
        matches = parse_file(file, 'Assert recognition validation...')
        for item in matches:
            print(item)
        if not any("Assert recognition validation" in item for item in matches):
            print("Error")
            errors +=1
        elif any ("Assert recognition validation... Failed!" in item for item in matches):
            print("Fail")
            failed += 1
        else:
            print("Pass")
            passed += 1
    print("Error cases count is",errors)
    print("Passed cases count is",passed)
    print("Failed cases count is",failed)
    testsuite = ET.Element('testsuite', name='Smoke test', Tests=str(count), Failures=str(failed), Errors=str(errors), Passed=str(passed))
    for file in files:
        fp = open(file)
        log=(fp.read())
        fp.close()
        testname=re.sub(r'^.*?-test', '-test', file)
        testcase = ET.SubElement(testsuite, 'testcase', name=str(testname))
        if "Assert recognition validation" not in log or "Assert recognition validation... Failed!" in log:
            failure= ET.SubElement(testcase, 'failure')
            failure.text=log
    xmlstr = minidom.parseString(ET.tostring(testsuite)).toprettyxml(indent="   ")
    with open("JUnit.xml", "w") as f:
        f.write(xmlstr)
    
print("Fetching logs ....")
create_report()