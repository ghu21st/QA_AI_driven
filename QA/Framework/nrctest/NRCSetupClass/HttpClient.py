"""
QA Http Test Client

"""
import io
import os
import sys
import requests
import base64
import time
import socket
import json
import random
import logging
import ssl
import threading
from TestContext import TestContext
import functools
import traceback

# Suppress known certificate warning from NRC test with secure connection https via urllib3 package - optional
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# +++++ timeout and exception +++++++++++
class TimeoutException(Exception):
    pass


def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [TimeoutException('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e

            t = threading.Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                # print 'error starting thread'
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return deco


# ++++++++++ NRC core test class ++++++++++++++++++
class HttpClient:

    @timeout(20)
    def __init__(self, https_port=9001, http_port=9000):
        # ------- initialize http client -------------
        context = TestContext()
        self._hostname_ = ""
        self._url_ = ""
        self._port_ = 0
        self.secure_connect = False
        logger = logging.getLogger(__name__)

        # ---- Define non-secure connection via http test client
        if 'httpPort' in context.config:
            self._http_port = context.config['httpPort']
            self.secure_connect = False
            #
            if 'NRCServer' in context.config:
                # for NRC host
                self._hostname_ = context.config['NRCServer']
                self._http_url = 'http://{}:{}'.format(
                    context.config['NRCServer'], self._http_port)
            else:
                self._hostname_ = socket.gethostname()
                self._http_url = 'http://{}:{}'.format(
                    socket.gethostname(), self._http_port)
            #
            self._port_ = self._http_port
            self._url_ = self._http_url

        # ----- Define secure connection via https test client -------------
        elif 'httpsPort' in context.config:
            self._https_port = context.config['httpsPort']
            self.secure_connect = True
            #
            if 'NRCServer' in context.config:
                # for NRC host
                self._hostname_ = context.config['NRCServer']
                self._https_url = 'https://{}:{}'.format(
                    context.config['NRCServer'], self._https_port)
            else:
                self._hostname_ = socket.gethostname()
                self._https_url = 'https://{}:{}'.format(
                    socket.gethostname(), self._https_port)
            #
            self._port_ = self._https_port
            self._url_ = self._https_url

        # ---- default using non-secure connection ------
        else:
            self._http_port = http_port
            self._hostname_ = socket.gethostname()
            self._url_ = 'http://{}:{}'.format(context.config['NRCServer'], self._http_port)
        #
        ret = "NRC http test client URL is: " + self._url_ + "\n"
        # print(ret)
        logger.info(ret)

        # Get the NRC test resource URL
        self._NRCTestResURL = context.config['NRCTestResURL']
        ret = "NRC test resource URL: " + self._NRCTestResURL + "\n"
        logger.info(ret)

        # define common used test parameters
        self.http = {}
        self.https = {}
        self.cert_verify = False
        self.cert = ()

        self.requests = {}
        self.responses = {}
        self.messagesList = []
        self.errorsList = []

        ret = "http test cient initialized.\n"
        # print(ret)
        logger.info(ret)

    @property
    def hostname(self):
        # return test server hostname
        return self._hostname_

    @property
    def port(self):
        # return test server port
        return self._port_

    @property
    def registerAPI(self):
        # return register Engines API
        return "registerEngine"

    @property
    def NRCTestResURL(self):
        '''Get the base NRC test resource URL'''
        return self._NRCTestResURL

    # ----------------------------
    @property
    def test_url(self):
        '''Get the base HTTP URL of the application server.'''
        return self._url_

    @property
    def allocateAPI(self):
        # return engine allocation API
        return "getResource"

    @property
    def getNRCTestResFileURL(self, testFile=None):
        if None == testFile:
            testFile = ''
        resURL = self._NRCTestResURL + '/' + testFile
        # print('NRC test resource file URL: ' + resURL)
        return resURL

    # ----- http test client via non-secure connection -----
    def connectHttp(self):
        # flag secure connection (true) or not (false)
        self.secure_connect = False

        # Using session object for http request client to persist certain params across requests
        self.http = requests.Session()
        #
        logger = logging.getLogger(__name__)
        logger.info("Connecting via non-secure http to server: " + self._http_url + '\n')

    # ---- https test client via secure connection -------
    def connectHttps(self, certFilePath=None):
        # flag secure connection (true) or not (false)
        self.secure_connect = True

        # check cert
        if None == certFilePath:
            self.cert_verify = False
        else:
            self.cert_verify = certFilePath

        # Using session object for http request client to persist certain params across requests
        self.https = requests.Session()
        self.https.verify = self.cert_verify
        #
        logger = logging.getLogger(__name__)
        logger.info("Connecting via secure https to server: " + self._https_url + '\n')

    # ---- Send request GET method ----------
    def requestGET(self, cmd=None):
        # NRC request GET method core test function
        # Input GET request param cmd URL; output return a list (status_code, response_body): if status_code <0, failed/exceptions;
        logger = logging.getLogger(__name__)
        #
        try:
            # check http or https client connect
            if self.secure_connect:
                response = self.https.get(cmd)
            else:
                response = self.http.get(cmd)
            #
            message = "\nSending GET request: " + cmd
            message += "\nRequest response: \n" + response.text
            message += "\nRequest response status code: \n" + str(response.status_code)
            logger.info(message)

            # check if response status code == 200, return response.json(); otherwise, return response.text
            if response.status_code == 200:
                return response.status_code, response.json()
            else:
                return response.status_code, response.text
        #
        except requests.exceptions.SSLError:
            message = "\nError! HTTP secure connection - SSL failed!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.ConnectionError:
            message = "\nError! Connect to http server failed!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.HTTPError:
            message = "\nError! HTTP GET request test failed!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.Timeout:
            message = "\nError! HTTP GET request timeout!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.RequestException as e:
            message = "\nError! Get request found unxpected exceptions!\n" + e.args[0] + '\n'
            logger.info(message)
            # raise  # note: no need to raise exception, since negative case need assertion check exception message if expected to pass test
            return -1, message

    # ----- Send request POST method --------
    def requestPOST(self, requestURL=None, requestBody=None, requestHeaders=None):
        # NRC request POST method core test function
        # Input POST request param body; output return a list (status_code, response_body): if status_code <0, failed/exceptions;
        logger = logging.getLogger(__name__)
        #
        try:
            # check http or https client connect
            if self.secure_connect:
                response = self.https.post(url=requestURL, data=json.dumps(requestBody), headers=requestHeaders)
            else:
                response = self.http.post(url=requestURL, data=json.dumps(requestBody), headers=requestHeaders)

            logger.info("\nSending POST request\nTest URL: " + requestURL + '\nTest Body:\n' + json.dumps(
                requestBody) + '\nTest Headers:\n' + json.dumps(requestHeaders))
            logger.info("\nRequest response:\n" + "Satus code: " + str(
                response.status_code) + '\n' + 'response text: ' + response.text)
            #
            return response.status_code, response.text
        #
        except requests.exceptions.SSLError:
            message = "\nError! HTTP secure connection - SSL failed!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.ConnectionError:
            message = "\nError! Connect to http server failed!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.HTTPError:
            message = "\nError! Http GET request test failed!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.Timeout:
            message = "\nError! Http GET request timeout!\n"
            logger.info(message)
            return -1, message
        except requests.exceptions.RequestException as e:
            message = "\nError! Get request found unxpected exceptions!\n" + e.args[0] + '\n'
            logger.info(message)
            # raise  # note: no need to raise exception, since negative case need assertion check exception message if expected to pass test
            return -1, message

    # ----- clean up /close test client
    def cleanup(self, sessionId=None):
        # print "Close http connection"
        if self.secure_connect:
            self.https.close()
            ret = 'Closed https test client secure connection\n'
        else:
            self.http.close()
            ret = 'Closed http test client connection\n'

        # print "Cleaning up."
        logger = logging.getLogger(__name__)
        logger.info(ret)
        time.sleep(
            5)  # need to set value greater than NRC core engine settings 'sessionDurationMsec', for stable engine multiple instances regression test

    '''
    *************************************************
    Engine allocation - 'GET'
    - Krypton:
        getResource?engineName=KRYPTON&lang=<language>&topic=<dpTopic>&version=<dpVersion>
    - NLE:
        getResource?engineName=NLE&requestType=Load&modelId=<modelId>&pipelineName=<pipelineName>&pipelineVersion=<pipelineVersion>
    - NTPE :
        getResource?engineName=NTPE&lang=ndp-<language>-<dpTopic>&version=<dpVersion>
    *************************************************
    '''

    def formatAllocateKryptonCmd(self, lang=None, topic=None, version=None):
        # NRC allocation for Krypton engine command URI, note: use default value for not defined input param
        retCmdURL = self.allocateAPI + '?' + 'engineName=' + 'KRYPTON'

        if None == lang:
            lang = 'eng-USA'  # default
        if None == topic:
            topic = 'GEN'  # default
        if None == version:
            version = '3.7.1'  # default
        #
        retCmdURL = retCmdURL + '&' + 'lang=' + lang + '&' + 'topic=' + topic + '&' + 'version=' + version

        logger = logging.getLogger(__name__)
        logger.info("Get NRC Krypton engine allocation command URL:\n " + retCmdURL + '\n')

        return retCmdURL

    def formatAllocateNLECmd(self, requestType=None, modelId=None, pipelineName=None, pipelineVersion=None):
        # NRC allocation for NLE engine command URI, note: use default value for not defined input param
        # note: for SS11 NR11, requestType='Load' always, after checked with DEV which hardcoded in NLPS as well.
        retCmdURL = self.allocateAPI + '?' + 'engineName=' + 'NLE'

        if None == requestType:
            requestType = 'Load'  # default, need to be fixed value as 'Load', since NLPS hardcoded it as well which always set as 'Load' by design
        if None == modelId:
            modelId = 'DomainName-ProjectName-eng-USA-1.2.3'  # default
        if None == pipelineName:
            pipelineName = 'QuickNLP'  # default
        if None == pipelineVersion:
            pipelineVersion = '2.6.5'  # default

        retCmdURL = retCmdURL + '&' + 'requestType=' + requestType + '&' + 'modelId=' + modelId + '&' + 'pipelineName=' + pipelineName + '&' + 'pipelineVersion=' + pipelineVersion

        logger = logging.getLogger(__name__)
        logger.info("Get NRC NLE engine allocation command URL:\n " + retCmdURL + '\n')

        return retCmdURL

    def formatAllocateNTPECmd(self, lang=None, version=None, modelId=None):
        # NRC allocation for NTpE engine command URI, note: use default value for not defined input param
        retCmdURL = self.allocateAPI + '?' + 'engineName=' + 'NTPE'

        if None == lang:
            lang = 'ndp-eng-USA-GEN'  # default
        if None == version:
            version = '3.7.1'  # default
        if None == modelId:
            modelId = 'DomainName-ProjectName-eng-USA-1.2.3'  # default (optional)

        retCmdURL = retCmdURL + '&' + 'lang=' + lang + '&' + 'version=' + version + '&' + 'modelId=' + modelId

        logger = logging.getLogger(__name__)
        logger.info("Get NRC NTpE engine allocation URL: " + retCmdURL + '\n')

        return retCmdURL

    def getNRCEngineAllocationKrypton(self, requestCmd=None):
        # get NRC engine - Krypon allocation
        if None == requestCmd:
            requestCmd = self.formatAllocateKryptonCmd()  # default

        cmd_url = self.test_url + '/' + requestCmd
        #
        response = self.requestGET(cmd=cmd_url)
        #
        return response

    def getNRCEngineAllocationNLE(self, requestCmd=None):
        # get NRC engine - NLE allocation
        if None == requestCmd:
            requestCmd = self.formatAllocateNLECmd()  # default

        cmd_url = self.test_url + '/' + requestCmd
        #
        response = self.requestGET(cmd=cmd_url)
        #
        return response

    def getNRCEngineAllocationNTPE(self, requestCmd=None):
        # get NRC engine - NTPE allocation
        if None == requestCmd:
            requestCmd = self.formatAllocateNTPECmd()  # default

        cmd_url = self.test_url + '/' + requestCmd
        #
        response = self.requestGET(cmd=cmd_url)
        #
        return response

    '''
    *************************************************
    Engine register - 'POST'
    - Krypton:
        {"engineName":"KRYPTON","address":{"host":"mtl-nr11mw-vm51","port":8600,"supportedProtocols":["ws"],"secure":true},"capabilities":[{"LP":"eng-USA","topic":"GEN","version":"3.7.1"}]}
    - NLE:
        {"engineName":"NLE","pipelineProviders":[{"name":"QuickNLP","version":"2.6.18"}],"address":{"host":"mtl-nr11mw-vm51","port":9091,"supportedProtocols":["ws","http"],"secure":true},"capabilities":[{"modelId":"DomainName-ProjectName-eng-USA-1.2.3"}]}
    - NTPE :
        {"engineName":"NTPE","address":{"host":"mtl-nr11mw-vm51","port":9092,"supportedProtocols":["wss","https"],"secure":true},"capabilities":{"glms":[{"language":"ndp-eng-USA-GEN","version":"3.7.1"}]}}
    *************************************************
    '''

    # format NRC register engine - Krypton post request
    def formatRegisterEngineKryptonCmd(self, hostname=None, port=None, LP=None, topic=None, version=None):
        # format NRC register engine for Krypton body object, note: use default value for not defined input param
        result = {"engineName": "KRYPTON"}
        # ------------
        tempObj1 = {}
        if None == hostname:
            hostname = self.hostname
        if None == port:
            port = 8600  # default KR port
        #
        tempObj1["host"] = hostname
        tempObj1["port"] = port
        tempObj1["supportedProtocols"] = ["ws"]
        tempObj1["secure"] = True
        #
        result["address"] = tempObj1
        # print(result)
        # ----------------
        tempObj2 = {}
        if None == LP:
            LP = 'eng-USA'  # default
        if None == topic:
            topic = 'GEN'  # default
        if None == version:
            version = '3.7.1'  # default
        #
        tempObj2["LP"] = LP
        tempObj2["topic"] = topic
        tempObj2["version"] = version
        #
        result["capabilities"] = []
        result["capabilities"].append(tempObj2)
        #
        result = json.dumps(result)  # convert formated request body to json string
        logger = logging.getLogger(__name__)
        logger.info("POST NRC register engine for Krypton: \n " + result + '\n')
        #
        result = json.loads(result)  # convert formated json string to json
        # print(result)
        return result

    # format NRC register engine - NLE request
    def formatRegisterEngineNLECmd(self, hostname=None, port=None, modelId=None, pipelineName=None,
                                   pipelineVersion=None):
        # format NRC register engine for Krypton body object, note: use default value for not defined input param
        result = {"engineName": "NLE"}
        # ------------
        tempObj1 = {}
        if None == hostname:
            hostname = self.hostname
        if None == port:
            port = 9090  # default NLE port
        #
        tempObj1["host"] = hostname
        tempObj1["port"] = port
        tempObj1["supportedProtocols"] = ["ws", "http"]
        tempObj1["secure"] = True
        #
        result["address"] = tempObj1
        # print(result)
        # ----------------
        tempObj2 = {}
        if None == pipelineName:
            pipelineName = 'eng-USA'  # default
        if None == pipelineVersion:
            pipelineVersion = '3.7.1'  # default
        #
        tempObj2["name"] = pipelineName
        tempObj2["version"] = pipelineVersion
        #
        result["pipelineProviders"] = []
        result["pipelineProviders"].append(tempObj2)
        # ----------------
        tempObj3 = {}
        if None == modelId:
            modelId = 'DomainName-ProjectName-eng-USA-1.2.3'  # default
        #
        tempObj3["modelId"] = modelId
        #
        result["capabilities"] = []
        result["capabilities"].append(tempObj3)
        # ------------------------
        result = json.dumps(result)  # convert formated request body to json string
        logger = logging.getLogger(__name__)
        logger.info("POST NRC register engine for NLE: \n " + result + '\n')
        #
        result = json.loads(result)  # convert formated json string to json
        # print(result)
        return result

    # format NRC register engine - NTpE request
    def formatRegisterEngineNTPECmd(self, hostname=None, port=None, language=None, version=None):
        # format NRC register engine for Krypton body objectd, note: use default value for not defined input param
        result = {"engineName": "NTPE"}
        # ------------
        tempObj1 = {}
        if None == hostname:
            hostname = self.hostname
        if None == port:
            port = 9095  # default NTpE port
        #
        tempObj1["host"] = hostname
        tempObj1["port"] = port
        tempObj1["supportedProtocols"] = ["wss", "https"]
        tempObj1["secure"] = True
        #
        result["address"] = tempObj1
        # print(result)
        # ----------------
        tempObj2 = {}
        if None == language:
            language = 'ndp-eng-USA-GEN'  # default
        if None == version:
            version = '3.7.1'  # default
        #
        tempObj2["language"] = language
        tempObj2["version"] = version
        # ---------------------
        tempObj3 = {"glms": []}
        tempObj3["glms"].append(tempObj2)
        #
        result["capabilities"] = tempObj3
        #
        result = json.dumps(result)  # convert formated request body to json string
        logger = logging.getLogger(__name__)
        logger.info("POST NRC register engine for NTPE: \n " + result + '\n')
        #
        result = json.loads(result)  # convert formated json string to json
        # print(result)
        return result

    # ---------------------------------------------------
    # send post request to register Engine - Krypton
    def postRegisterEngineKrypton(self, requestURL=None, requestBody=None, requestHeaders=None):
        # POST method API to register core engine
        if None == requestURL:
            requestURL = self.test_url + '/' + self.registerAPI  # default test URL with API for post request
        if None == requestHeaders:
            requestHeaders = {  # default post request headers
                'Accept': '*/*',
                'content-type': 'application/json'
            }
        if None == requestBody:
            requestBody = self.formatRegisterEngineKryptonCmd()  # default post request test body (payload)
        #
        logger = logging.getLogger(__name__)
        logger.info(
            "Sending POST request to regiser engine - Krypton:\nTest URL: " + requestURL + '\nTest Body:\n' + json.dumps(
                requestBody) + '\nTest Headers:\n' + json.dumps(requestHeaders))
        #
        response = self.requestPOST(requestURL=requestURL, requestBody=requestBody, requestHeaders=requestHeaders)
        retStr = "POST request responses:\n" + 'status code: ' + str(response[0]) + '\n' + 'response text: ' + response[
            1] + '\n'
        logger.info("Received POST responses:\n" + retStr + '\n')
        #
        return response

    # send post request to register Engine - NLE
    def postRegisterEngineNLE(self, requestURL=None, requestBody=None, requestHeaders=None):
        # POST method API to register core engine
        if None == requestURL:
            requestURL = self.test_url + '/' + self.registerAPI  # default test URL with API for post request
        if None == requestHeaders:
            requestHeaders = {  # default post request headers
                'Accept': '*/*',
                'content-type': 'application/json'
            }
        if None == requestBody:
            requestBody = self.formatRegisterEngineNLECmd()  # default post request test body (payload)
        #
        logger = logging.getLogger(__name__)
        logger.info(
            "Sending POST request to regiser engine - NLE:\nTest URL: " + requestURL + '\nTest Body:\n' + json.dumps(
                requestBody) + '\nTest Headers:\n' + json.dumps(requestHeaders))
        #
        response = self.requestPOST(requestURL=requestURL, requestBody=requestBody, requestHeaders=requestHeaders)
        retStr = "POST request responses:\n" + 'status code: ' + str(response[0]) + '\n' + 'response text: ' + response[
            1] + '\n'
        #
        logger.info("Received POST responses:\n" + retStr + '\n')

        return response

    # send post request to register Engine - NTPE
    def postRegisterEngineNTPE(self, requestURL=None, requestBody=None, requestHeaders=None):
        # POST method API to register core engine
        if None == requestURL:
            requestURL = self.test_url + '/' + self.registerAPI  # default test URL with API for post request
        if None == requestHeaders:
            requestHeaders = {  # default post request headers
                'content-type': 'application/json'
            }
        if None == requestBody:
            requestBody = self.formatRegisterEngineNTPECmd()  # default post request test body (payload)
        #
        logger = logging.getLogger(__name__)
        logger.info(
            "Sending POST request to regiser engine - NTPE:\nTest URL: " + requestURL + '\nTest Body:\n' + json.dumps(
                requestBody) + '\nTest Headers:\n' + json.dumps(requestHeaders))
        #
        response = self.requestPOST(requestURL=requestURL, requestBody=requestBody, requestHeaders=requestHeaders)
        retStr = "POST request responses:\n" + 'status code: ' + str(response[0]) + '\n' + 'response text: ' + response[
            1] + '\n'
        logger.info("Received POST responses:\n" + retStr + '\n')
        #
        return response

    # -------------- For compatible or useful functions with websocket test framework --------------
    def genRequestId(self):
        x = random.randint(10000000, 99999999)
        # print x
        reqId = str(x) + "-97a2-11e6-9346-fde5d2234523"
        return reqId

    def genSessionId(self):
        x = random.randint(10000000, 99999999)
        # print x
        sessionId = str(x) + "-912e-11e6-b83e-3f30a2b99389"
        return sessionId

    def printMessagesList(self):
        i = 0
        for messages in self.messagesList:
            message = json.loads(messages)
            ## print "message " + str(i) + "\'s requestId is: " + message
            # print "message " + str(i) + " is: " + str(message['body'])
            i = i + 1

    def printErrorsList(self):
        i = 0
        for errors in self.errorsList:
            error = json.loads(errors)
            ## print "message " + str(i) + "\'s requestId is: " + message
            # print "error " + str(i) + " is: " + str(error['body'])
            i = i + 1

    @staticmethod
    def traceback():
        stack = sys.exc_info()
        traceback.print_tb(stack[2])
        # Format Stack Trace
        extractedTB = traceback.extract_tb(stack[2], limit=1)[0]
        lineNumber = extractedTB[1]
        testName = extractedTB[2]
        lineContent = extractedTB[3]
        realStack = str(stack)
        formattedTest = "\nTest Name: " + testName + "\nLine Number: " + str(
            lineNumber) + "\nLine Content: " + lineContent + "\nStack Trace: " + realStack
        return formattedTest
