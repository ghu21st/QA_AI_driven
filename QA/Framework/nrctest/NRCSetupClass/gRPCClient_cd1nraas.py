"""
QA gRPC test Client for NRC/NRaaS

"""
import io
import os
import sys
import requests
import time
from datetime import datetime
import socket
import json
import random
import logging
import ssl
import threading
from TestContext import *
import functools
import traceback
import re
from urllib.parse import urlparse
import wave
import urllib

import grpc
from nrc_pb2 import *
from nrc_pb2_grpc import *

# from nrc_pb2 import RecognitionRequest, AudioFormat, EnumResultFormat, RecognitionInit, RecognitionParameters, ResultFormat, RecognitionResource, ULaw, ALaw, PCM
# from nrc_pb2_grpc import NRCStub

# Suppress known certificate warning from NRC test with secure connection gRPCs via urllib3 package - optional
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


# ++++++++++ NRC gRPC core test class ++++++++++++++++++
class gRPCClient:
    # _audioBufms_: int

    @timeout(50)
    def __init__(self, gRPC_server=None, gRPCs_port=None, gRPC_port=None):
        # ------- initialize gRPC client -------------
        context = TestContext()
        self._hostname_ = ''
        self._url_ = ''
        self._secure_url_ = ''
        self._port_ = 0
        self.secure_connect = False
        self._logger_ = logging.getLogger(__name__)

        # Get the NRC test logging level
        self._logging_ = context.config['NRCTestLogging']
        msg = 'NRC QA test logging level: ' + str(self._logging_)
        self._logger_.info(msg)

        # Get NRCTest, boolean, if True -> NRC test (default), if False -> NRaaS test
        if context.config['NRCTest']:
            self._nrctest_ = True
        else:
            self._nrctest_ = False

        # Get NRCServiceURL, must have for NRaaS test when self._nrctest_ == False
        if 'NRCServiceURL' in context.config:
            self._serviceurl_ = context.config['NRCServiceURL']
        else:
            self._serviceurl_ = ''

        # Get the NRC request metadata
        self._metadata_ = context.config['NRCTestMetadata']
        if self._metadata_ != "None":
            # Converting into list of tuple
            tmp = []
            [tmp.append((k, v)) for k, v in self._metadata_.items()]
            self._metadata_ = tmp
        else:
            self._metadata_ = None
        if context.config['GAurl']:
            self._globalauthurl_ = context.config['GAurl']
        else:
            self._globalauthurl_ = ""
        # For NRC service IP or gRPC server. priority: 1) custom input; 2) config file; 3) default localhost
        if gRPC_server is not None:
            self._hostname_ = gRPC_server
        elif 'NRCServiceIP' in context.config:
            self._hostname_ = context.config['NRCServiceIP']
        else:
            self._hostname_ = socket.gethostname()
        msg = 'NRC gRPC test service/server: ' + self._hostname_ + '\n'
        if self._logging_ > 1:
            print(msg)
        self._logger_.info(msg)

        # For NRC test server port
        if 'NRCSecureServicePort' in context.config:
            self._secure_port_ = context.config['NRCSecureServicePort']
        else:
            self._secure_port_ = 50052
        if 'NRCServicePort' in context.config:
            self._port_ = context.config['NRCServicePort']
        else:
            self._port_ = 50051

        # For NRC gRPC secure test check. Priority high to low for secure connect:
        #   1) Global secure config settings NRCTestSecureConnect;
        #   2) Test client Class init param with secure gRPCs_port assigned;
        #   3) Global port config settings (secure first then insecure);
        #   4) default - insecure (no other secure settings)
        #
        # Priority 1: check global config settings
        if 'NRCTestSecureConnect' in context.config:
            self.secure_connect = context.config['NRCTestSecureConnect']
        else:
            self.secure_connect = False

        # Priority 2: check gRPCClient class init
        if not self.secure_connect:
            if gRPCs_port is not None:
                self._port_ = gRPCs_port
                self.secure_connect = True
            elif gRPC_port is not None:
                self._port_ = gRPC_port
                self.secure_connect = False
            else:
                # Priority 3: check global port settings (secure first then insecure)
                if 'NRCSecureServicePort' in context.config:
                    self.secure_connect = True
                elif 'NRCsServicePort' in context.config:
                    self.secure_connect = False
                else:
                    # Priority 4: default insecure
                    #self._port_ = 30051
                    self.secure_connect = False

        # check if for NRaaS test, note: always secure connect
        if not self._nrctest_:
            # For secure gRPC connection with global auth------------
            ssl_credentials = grpc.ssl_channel_credentials()     # for test with Global Auth token
            tmp_token = self.get_GAtoken()
            #msg += '\nGet global auth token: ' + tmp_token
            call_credentials = grpc.access_token_call_credentials(tmp_token)
            self._credentials_ = grpc.composite_channel_credentials(ssl_credentials, call_credentials)

            msg += '\nChannel credentials: ' + str(self._credentials_)

            # For gRPC secure url for NRaaS testing
            self._parse_url_ = urlparse(self._serviceurl_)
            msg += '\nService URL: ' + str(self._serviceurl_)
            msg += '\nParsed URL: ' + str(self._parse_url_)
            self._secure_port_ = self._parse_url_.port

            # set secure_connect to true for NRaaS test
            self.secure_connect = True

            # get secure_port
            if self._secure_port_ is None:
                self._secure_port_ = 443 if url.scheme == 'https' else 80
            msg += '\nService port: ' + str(self._secure_port_)

            # Get real secure URL
            self._secure_url_ = '{}:{}'.format(self._parse_url_.hostname, self._secure_port_)
            msg += '\nNRaaS secure URL is: ' + str(self._secure_url_) + '\n'
            if self._logging_ > 1:
                print(msg)
            self._logger_.info(msg)

        # check if for NRC test with secure connect
        elif self.secure_connect and self._nrctest_:
            # For secure gRPC connection ------------
            # Get certificate for nrc secure connection
            with open('/QA/NRC_Test/Framework/nrctest/NRCSetupClass/nrc.crt', 'rb') as certFile:
                trust_certs = certFile.read()
                print('\nNRC certificate content:\n' + str(trust_certs))  # for debug
            certFile.close()

            # For gRPC channel via secure connection
            self._credentials_ = grpc.ssl_channel_credentials(root_certificates=trust_certs)

            # For gRPC secure url [Note: for secure connection, using nrc:port as url, not insecure connection using hostname:port as url)
            self._secure_url_ = '{}:{}'.format(self._hostname_, self._secure_port_)
            self._url_ = self._secure_url_
            msg = '\nNRC gRPC test server secure URL is: ' + self._secure_url_ + '\n'
            msg += 'NRC gRPC test port: ' + str(self._secure_port_) + '\n'
            if self._logging_ > 1:
                print(msg)
            self._logger_.info(msg)

        # otherwise, insecure test for NRC
        else:
            # For insecure gRPC connection -------------
            # self._url_ = 'http://{}:{}'.format(self._hostname_, self._port_)
            self._url_ = '{}:{}'.format(self._hostname_, self._port_)
            #
            msg = 'NRC gRPC test server URL is: ' + self._url_ + '\n'
            msg += 'NRC gRPC test port: ' + str(self._port_) + '\n'
            if self._logging_ > 1:
                print(msg)
            self._logger_.info(msg)

        # Get the NRC test resource URL
        self._NRCTestResURL_ = context.config['NRCTestResURL']
        msg = 'NRC test resource URL: ' + self._NRCTestResURL_ + '\n'
        if self._logging_ > 1:
            print(msg)

        # Get the NRC test resource secure URL
        self._NRCTestResURLSecure_ = context.config['NRCTestResURLSecure']
        msg = 'NRC test resource secure URL: ' + self._NRCTestResURLSecure_ + '\n'
        if self._logging_ > 1:
            print(msg)

        self._logger_.info(msg)

        # Get the NRC test audio path
        self._audio_path_ = context.config['NRCAudioPath']
        msg = 'NRC test audio path: ' + self._audio_path_ + '\n'
        if self._logging_ > 1:
            print(msg)
        self._logger_.info(msg)

        # define NRC test parameters/variables
        self.cert_verify = False
        self._cert_file_ = ''
        self._creds_ = {}
        self._channel_ = {}

        self._audio_format_ = {}
        self._recog_grammar_ = {}
        self._uri_grammar_params_ = {}
        self._recog_params_ = {}
        self._recog_resultFormat_ = {}
        self._recog_res_ = {}
        self._recog_init_ = {}
        
        self._dtmfrecog_params_ = {}
        self._dtmfrecog_init_ = {}

        self._requests_ = {}
        self._responses_ = {}
        self.messagesList = []
        self.errorsList = []

        # for global audio parameters/settings: path, buffer ms or interval, xrate
        if 'NRCAudioPath' in context.config:
            self._audio_path_ = context.config['NRCAudioPath']
        else:
            self._audio_path_ = '/QA/NRC_Test/Framework/nrctest/audio/'  # default value
        if 'NRCAudioBufms' in context.config:
            self._audioBufms_ = context.config['NRCAudioBufms']
        else:
            self._audioBufms_ = 30  # default 30 ms
        if 'NRCAudioXrate' in context.config:
            self._audioXrate_ = context.config['NRCAudioXrate']
        else:
            self._audioXrate_ = 1.0  # default 30 ms
        self._audioBytesPerMs_ = 8  # default bytes per ms for ulaw/alaw, 8-bit 8 kHz, =8; for pcm, 16-bit 8kHz, =16
        self._audioChunkSize_ = 240  # default chunk size (bytes) for ulaw/alaw

        # for QA test re-run/re-try parameters / settings
        if 'NRCTestRetryNum' in context.config:
            self._testRetryNum_ = context.config['NRCTestRetryNum']
        else:
            self._testRetryNum_ = 3  # default test retry number: 3
        if 'NRCTestRetryWaitSec' in context.config:
            self._testRetryWait_ = context.config['NRCTestRetryWaitSec']
        else:
            self._testRetryWait_ = 5  # default wait settings: 5 sec
        #
        msg = 'gRPC test client initialized.\n'
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)
        time.sleep(1)

    @property
    def hostname(self):
        # return test server hostname
        return self._hostname_

    @property
    def port(self):
        # return test server port
        return self._port_

    @property
    def test_res_url(self):
        # Get the base NRC test resource URL
        return self._NRCTestResURL_

    @property
    def test_res_url_secure(self):
        # Get the secure NRC test resource URL
        return self._NRCTestResURLSecure_

    @property
    def test_url(self):
        # Get the base gRPC URL of the application server
        return self._url_

    @property
    def test_secure_connect(self):
        # Get secure_connect return
        return self.secure_connect

    @property
    def get_logger(self):
        # return test logger
        return self._logger_
    
    @property
    def test_metadata(self):
        # return test metadata set in the yaml testServerConfig file
        return self._metadata_

    # ----------------------------
    def getNRCTestResFileURL(self, testFile=None):
        if None == testFile:
            testFile = ''
        resURL = self._NRCTestResURL_ + testFile
        msg = 'NRC test resource file URL: ' + resURL
        if self._logging_ > 0:
            print(msg)
        # log info
        self._logger_.info(msg)
        return resURL

    def getNRCTestResFileSecureURL(self, testFile=None):
        if None == testFile:
            testFile = ''
        resURL = self._NRCTestResURLSecure_ + testFile
        msg = 'NRC test resource file secure URL: ' + resURL
        if self._logging_ > 0:
            print(msg)
        # log info
        self._logger_.info(msg)
        return resURL

    # ----- gRPC test client via non-secure connection -----
    def connectgRPC(self):
        # flag secure connection (true) or not (false)
        self.secure_connect = False
        msg = 'Connecting via non-secure gRPC to server: ' + self._url_ + '\n'
        if self._logging_ > 0:
            print(msg)

        # connect gRPC via insecure channel
        self._channel_ = grpc.insecure_channel(self._url_)

        # log info
        self._logger_.info(msg)
        time.sleep(1)

        # return nrc_stub
        return self._channel_

    # ---- gRPCs test client via secure connection -------
    def connectgRPCs(self, certFilePath=None):
        # flag secure connection (true) or not (false)
        self.secure_connect = True
        msg = 'Connecting via secure gRPC to server: ' + self._url_ + '\n'

        # cert
        cert = open(os.path.expanduser(self._cert_file_), 'rb').read()
        self._creds_ = grpc.ssl_channel_credentials(cert)

        # check cert
        if None == certFilePath:
            self.cert_verify = False
        else:
            self.cert_verify = certFilePath

        # Connect gRPC via secure channel
        self._channel_ = grpc.secure_channel(self._url_, self.cert_verify)
        # self._channel_ = grpc.secure_channel(self._url_, self._creds_)

        # log info
        self._logger_.info(msg)
        time.sleep(1)
        #
        return self._channel_

    # ----- clean up /close test client
    def cleanup(self):
        if self.secure_connect:
            msg = 'Close gRPCs test client secure connection\n'
        else:
            msg = 'Close gRPC test client connection\n'

        self._channel_.close()
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)
        time.sleep(2)  # need to set value greater than NRC core engine settings 'sessionDurationMsec', for stable test

    # ---- Get Global Auth token for NRaaS in CD1
    def get_GAtoken(self):

        # debug
        msg = '\nGlobal Auth settings: \n'
        #msg += 'url: ' + str(self._globalauthurl_) + '\n'
        #if self._logging_ > 0:
        #    print(msg)
        #    self._logger_.info(msg)

        # Define request data
        #data = {
        #    'aud': '97126656-6fbd-429d-9928-971e1acce36d',
        #    'oid': '071fc199-f3b5-4aed-8b5e-febd8c27d33a',
        #    'tid': '9f6be790-4a16-4dd6-9850-44a0d2649aef'
        #}
        #headers = {'ContentType': 'application/json'}
        # Get response
        #response = requests.post(self._globalauthurl_, json=data)
        #token = response.json()["access_token"]
        token=os.environ.get('NRAASTOKEN')
								 

        # update metadata list of tuples for NRaaS GA token
        # newTokenTuples = [('authorization', str(token))]
        # self._metadata_ += newTokenTuples
        # msg = '\nGet global auth token:'   # for debug
        # msg += str(token)                 # for debug
        # msg += '\n\nGet new metadata list of tuples: \n' + str(self._metadata_)

        # Logging
        if self._logging_ > 0:
            print(msg)
            self._logger_.info(msg)
        #
        return token

    # -------- Define a function for recognition init with input from other functions: RecognitionParameters and
    # audio format ----
    def audio_format(self, audioFormat=None):
        if audioFormat == 'ulaw' or audioFormat == 'ULAW':
            self._audio_format_ = 'ULaw'
            audio_format_ret = AudioFormat(ulaw=ULaw())
            self._audioBytesPerMs_ = 8  # ulaw: 8 bit, 8 kHz
        elif audioFormat == 'alaw' or audioFormat == 'ALAW':
            self._audio_format_ = 'ALaw'
            audio_format_ret = AudioFormat(alaw=ALaw())
            self._audioBytesPerMs_ = 8  # alaw: 8 bit, 8 kHz
        elif audioFormat == 'pcm' or audioFormat == 'PCM':
            self._audio_format_ = 'PCM'
            audio_format_ret = AudioFormat(pcm=PCM())
            self._audioBytesPerMs_ = 16  # pcm: 16 bit, 8 kHz
        else:  # default
            self._audio_format_ = 'ULaw'
            audio_format_ret = AudioFormat(ulaw=ULaw())
            self._audioBytesPerMs_ = 8  # ulaw: 8 bit, 8 kHz
        #
        msg = '\nTest audio format:' + str(self._audio_format_) + '\n'
        self._logger_.info(msg)
        if self._logging_ > 1:
            print(msg)
        #
        return audio_format_ret

    # -------- Define a function for recognition_flags
    def recognition_flags(self, stalltimers=None):
        if stalltimers == False:
            self._rec_flags_ = 'stall_timers = False'
        elif stalltimers == True:
            self._rec_flags_ = 'stall_timers = True'
        else:  # default
            stalltimers = False
            self._rec_flags_ = 'stall_timers = False'

        self.rec_flags_ret = RecognitionFlags(stall_timers=stalltimers)
        msg = '\nRecognition Flags: ' + str(self._rec_flags_) + '\n'
        self._logger_.info(msg)
        if self._logging_ > 0:
            print(msg)

        return self.rec_flags_ret

    # -------- Define a function for Control Message
    def recognition_control(self, rec_control_time=None):
        if None == rec_control_time:
            self.rec_control_time = None
        else:
            if rec_control_time == 0:
                self.rec_control_time = 0
                self.recognition_control_flag = True
            else:
                self.rec_control_time = rec_control_time+175
                self.recognition_control_flag = True

        return self.rec_control_time

    # Recognition Result Format ---
    def recognition_resultFormat(self, resultFormat=None, additionParams=None):
        # print('\nrecognition_resultFormat function input result format:' + str(resultFormat) + '\n')  # for debug

        if resultFormat == 'nlsml' or resultFormat == 'NLSML':
            resultFormat = EnumResultFormat.NLSML
            # resultFormat = 0
        elif resultFormat == 'emma' or resultFormat == 'EMMA':
            resultFormat = EnumResultFormat.EMMA
            # resultFormat = 1
        else:
            resultFormat = EnumResultFormat.NLSML  # set default
        #
        self._recog_resultFormat_ = ResultFormat(format=resultFormat, additional_parameters=additionParams)
        msg = '\nRecognition result format: ' + str(self._recog_resultFormat_) + '\n'
        if self._logging_ > 1:
            print(msg)
        #
        return self._recog_resultFormat_

    # Recognition Parameters ---
    def recognition_parameters(self, audioFormat=None, resultFormat=None, confLevel=None, nBest=None,
                               noInputTimeout=None, completeTimeout=None, incompleteTimeout=None, maxSpeechTimeout=None,
                               speechDetectionSensitivity=None, cookieSet=None, endpointerParameters=None,
                               recognizerParameters=None,
                               secureContextLevel=None, recognizerFlags=None):
        # print('\nrecognition_parameter function input result format:' + str(resultFormat) + '\n')

        # check & set default value -------
        if None == audioFormat:
            audioFormat = 'ulaw'  # default
        if None == resultFormat:
            resultFormat = 'nlsml'  # default
        if None == confLevel:
            confLevel = 0.5  # default
        if None == nBest:
            nBest = 2  # default
        if None == noInputTimeout:
            noInputTimeout = 7000  # default
        if None == completeTimeout:
            completeTimeout = 0  # default
        if completeTimeout == 'ignore':
            completeTimeout = None # Special case where we ignore completetimeout parameter in recongition so it doesn't overwrite grammar setting
        if None == incompleteTimeout:
            incompleteTimeout = 1500  # default
        if incompleteTimeout == 'ignore':
            incompleteTimeout = None # Special case where we ignore incompletetimeout parameter in recongition so it doesn't overwrite grammar setting
        if None == maxSpeechTimeout:
            maxSpeechTimeout = -1  # default
        if None == speechDetectionSensitivity:
            speechDetectionSensitivity = 0.5  # default 0.5

        # check secure context level parameter
        if secureContextLevel == 'OPEN':
            secureContextLevel = EnumSecureContextLevel.OPEN
        elif secureContextLevel == 'SUPPRESS':
            secureContextLevel = EnumSecureContextLevel.SUPPRESS
        else:
            secureContextLevel = EnumSecureContextLevel.OPEN  # set QA test default or none assigned secure context value to OPEN
        #
        audio_format = self.audio_format(audioFormat=audioFormat)
        result_format = self.recognition_resultFormat(resultFormat=resultFormat)
        recognition_flags = self.recognition_flags(stalltimers=recognizerFlags)        
        self._recog_params_ = RecognitionParameters(
            audio_format=audio_format,
            result_format=result_format,
            confidence_level=confLevel,
            nbest=nBest,
            no_input_timeout_ms=noInputTimeout,
            complete_timeout_ms=completeTimeout,
            incomplete_timeout_ms=incompleteTimeout,
            max_speech_timeout_ms=maxSpeechTimeout,
            speech_detection_sensitivity=speechDetectionSensitivity,
            cookies=cookieSet,
            endpointer_parameters=endpointerParameters,
            recognizer_parameters=recognizerParameters,
            secure_context_level=secureContextLevel,
            recognition_flags=recognition_flags
        )
        time.sleep(0.2)
        return self._recog_params_

    #Jyoti dtmfRecognition Parameters ---
    def dtmfrecognition_parameters(self,resultFormat=None, nBest=None,
                               noInputTimeout=None, dtmfTermTimeout =None, dtmfInterdigitTimeout =None, dtmfTermChar=None, cookieSet=None, 
                               recognizerParameters=None, secureContextLevel=None, recognizerFlags=None):
        # print('\nrecognition_parameter function input result format:' + str(resultFormat) + '\n')

        # check & set default value -------
        
        if None == resultFormat:
            resultFormat = 'nlsml'  # default
        if None == nBest:
            nBest = 2  # default
        if None == noInputTimeout:
            noInputTimeout = 7000  # default
        if None == dtmfTermTimeout:
            dtmfTermTimeout = 10000  # default
        if None == dtmfInterdigitTimeout:
            dtmfInterdigitTimeout = 5000 # Special case where we ignore completetimeout parameter in recongition so it doesn't overwrite grammar setting
        if None == dtmfTermChar:
            dtmfTermChar = '#'
        # check secure context level parameter
        if secureContextLevel == 'OPEN':
            secureContextLevel = EnumSecureContextLevel.OPEN
        elif secureContextLevel == 'SUPPRESS':
            secureContextLevel = EnumSecureContextLevel.SUPPRESS
        else:
            secureContextLevel = EnumSecureContextLevel.OPEN  # set QA test default or none assigned secure context value to OPEN
        
        result_format = self.recognition_resultFormat(resultFormat=resultFormat)
        recognition_flags = self.recognition_flags(stalltimers=recognizerFlags) 
               
        self._dtmfrecog_params_ = DTMFRecognitionParameters(
            recognition_flags=recognition_flags,
            no_input_timeout_ms=noInputTimeout,
            dtmf_interdigit_timeout_ms=dtmfInterdigitTimeout,
            dtmf_term_timeout_ms=dtmfTermTimeout,
            dtmf_term_char= dtmfTermChar,
            nbest=nBest,
            result_format=result_format,
            cookies=cookieSet,
            recognizer_parameters=recognizerParameters,
            secure_context_level=secureContextLevel
        )
        time.sleep(0.2)
        return self._dtmfrecog_params_

    # Recognition Parameters paasing through Swi parameter grammar
    def recognition_swiparameters(self, audioFormat=None, resultFormat=None, confLevel=None, nBest=None,
                                  noInputTimeout=None, completeTimeout=None, incompleteTimeout=None,
                                  maxSpeechTimeout=None,
                                  speechDetectionSensitivity=None, cookieSet=None, endpointerParameters=None,
                                  recognizerParameters=None, secureContextLevel=None, recognizerFlags=None):
        # check secure context level parameter
        if secureContextLevel == 'OPEN':
            secureContextLevel = EnumSecureContextLevel.OPEN
        elif secureContextLevel == 'SUPPRESS':
            secureContextLevel = EnumSecureContextLevel.SUPPRESS
        else:
            secureContextLevel = EnumSecureContextLevel.OPEN  # set QA test default or none assigned secure context value to OPEN

        audio_format = self.audio_format(audioFormat=audioFormat)
        result_format = self.recognition_resultFormat(resultFormat=resultFormat)
        recognition_flags = self.recognition_flags(stalltimers=recognizerFlags) 
        self._recog_params_ = RecognitionParameters(
            audio_format=audio_format,
            result_format=result_format,
            confidence_level=confLevel,
            nbest=nBest,
            no_input_timeout_ms=noInputTimeout,
            complete_timeout_ms=completeTimeout,
            incomplete_timeout_ms=incompleteTimeout,
            max_speech_timeout_ms=maxSpeechTimeout,
            speech_detection_sensitivity=speechDetectionSensitivity,
            cookies=cookieSet,
            endpointer_parameters=endpointerParameters,
            recognizer_parameters=recognizerParameters,
            secure_context_level=secureContextLevel,
            recognition_flags=recognition_flags 
        )
        time.sleep(0.2)  # for debug
        return self._recog_params_

    # Recognition grammars (internal) ----
    def recognition_grammars(self, grammarType=None, grammarData=None, mediaType=None):
        if None == grammarType:
            grammarType = 'builtin'
        #
        if grammarType == 'builtin':
            self._recog_grammar_ = 'builtin:grammar/' + grammarData
        elif grammarType == 'inline_grammar':
            self._recog_grammar_ = InlineGrammar(grammar=grammarData, media_type=mediaType)
        elif grammarType == 'uri_grammar':
            self._recog_grammar_ = UriGrammar(uri=grammarData, media_type=mediaType)
        else:
            self._recog_grammar_ = 'builtin:grammar/' + grammarData
        #
        return self._recog_grammar_

    # Recognition uri grammars (internal) ----
    def recognition_UriGrammarParam(self, requestTimeout=None, contentBase=None, maxAge=None, maxStale=None):
        if None == requestTimeout:
            requestTimeout = 0
        if None == contentBase:
            contentBase = ''
        if None == maxAge:
            maxAge = 0
        if None == maxStale:
            maxStale = 0
        #
        self._uri_grammar_params_ = UriGrammarParameters(request_timeout_ms=requestTimeout, content_base=contentBase,
                                                         max_age=maxAge, max_stale=maxStale)
        #
        return self._uri_grammar_params_

    # Recognition resource ---
    def recognition_resource(self, grammarType=None, grammarData=None, mediaType=None, languageIn=None,
                             grammarWeight=None, grammarId=None, uriParameters=None):
        if None == grammarType:
            grammarType = 'builtin'
        if None == grammarData:
            grammarData = 'digits'
        if None == languageIn:
            languageIn = 'en-US'
        if None == uriParameters:
            uriParameters = self.recognition_UriGrammarParam()

        if None == mediaType:
            mediaType = EnumMediaType.AUTOMATIC
        elif mediaType == "srgsxml":
            mediaType = EnumMediaType.APPLICATION_SRGS_XML
        elif mediaType == 'xswigrammar':
            mediaType = EnumMediaType.APPLICATION_X_SWI_GRAMMAR
        elif mediaType == 'xswiparameter':
            mediaType = EnumMediaType.APPLICATION_X_SWI_PARAMETER
        elif mediaType == 'automatic':
            mediaType = EnumMediaType.AUTOMATIC
        else:
            mediaType = EnumMediaType.AUTOMATIC

        msg = '\ngrammar type: ' + grammarType + ';  ' + ' grammar data: ' + grammarData + '   ' + ' media type: ' + str(
            mediaType) + ' language: ' + languageIn + '\n'
        self._logger_.info(msg)
        if self._logging_ > 1:
            print(msg)
        #
        if grammarType == 'builtin':
            self._recog_res_ = RecognitionResource(
                builtin='builtin:grammar/' + grammarData,
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
        if grammarType == 'builtin:dtmf':
            self._recog_res_ = RecognitionResource(
                builtin='builtin:dtmf/' + grammarData,
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
          
        elif grammarType == 'inline_grammar':
            self._recog_res_ = RecognitionResource(
                inline_grammar=InlineGrammar(grammar=grammarData.encode(), media_type=mediaType),
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
        elif grammarType == 'uri_grammar':
            self._recog_res_ = RecognitionResource(
                uri_grammar=UriGrammar(uri=grammarData, media_type=mediaType, parameters=uriParameters),
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
        else:
            test_grammar = 'builtin:grammar/' + grammarData
            self._recog_res_ = RecognitionResource(
                builtin=test_grammar,
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
        #
        time.sleep(0.2)  # for debug
        return self._recog_res_


    def dtmfrecognition_resource(self, grammarType=None, grammarData=None, mediaType=None, languageIn=None,
                             grammarWeight=None, grammarId=None, uriParameters=None):
        if None == grammarType:
            grammarType = 'builtin'
        if None == grammarData:
            grammarData = 'digits'
        if None == languageIn:
            languageIn = 'en-US'
        if None == uriParameters:
            uriParameters = self.recognition_UriGrammarParam()

        if None == mediaType:
            mediaType = EnumMediaType.AUTOMATIC
        elif mediaType == "srgsxml":
            mediaType = EnumMediaType.APPLICATION_SRGS_XML
        elif mediaType == 'xswigrammar':
            mediaType = EnumMediaType.APPLICATION_X_SWI_GRAMMAR
        elif mediaType == 'xswiparameter':
            mediaType = EnumMediaType.APPLICATION_X_SWI_PARAMETER
        elif mediaType == 'automatic':
            mediaType = EnumMediaType.AUTOMATIC
        else:
            mediaType = EnumMediaType.AUTOMATIC

        msg = '\ngrammar type: ' + grammarType + ';  ' + ' grammar data: ' + grammarData + '   ' + ' media type: ' + str(
            mediaType) + ' language: ' + languageIn + '\n'
        self._logger_.info(msg)
        if self._logging_ > 1:
            print(msg)
        #
        if grammarType == 'builtin':
            self._recog_res_ = RecognitionResource(
                builtin='builtin:dtmf/' + grammarData,
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
            
        elif grammarType == 'inline_grammar':
            self._recog_res_ = RecognitionResource(
                inline_grammar=InlineGrammar(grammar=grammarData.encode(), media_type=mediaType),
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
        elif grammarType == 'uri_grammar':
            self._recog_res_ = RecognitionResource(
                uri_grammar=UriGrammar(uri=grammarData, media_type=mediaType, parameters=uriParameters),
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
        else:
            test_grammar = 'builtin:grammar/' + grammarData
            self._recog_res_ = RecognitionResource(
                builtin=test_grammar,
                language=languageIn,
                weight=grammarWeight,
                grammar_id=grammarId
            )
        #
        time.sleep(0.2)  # for debug
        return self._recog_res_
        
    # ----------------------------------------
    # Define a function for recognition init with: RecognitionParameters & RecognitionResource (one resource only!)
    # audioFormat, builtinGrammar, resultFormat, confLevel language...etc
    def recognition_init(self, recogParam=None,
                         recogRes=None,
                         clientData=None,
                         user_id=None):  # note: only accept one recognition resource only here, for repeated recognition resource, see: recognition_init_repeated()
        # check & set default value -------
        if None == recogParam:
            recogParam = self.recognition_parameters()
        if None == recogRes:
            recogRes = self.recognition_resource()
        #
        msg = ''
        msg += 'recognition parameters: \n' + str(recogParam)
        msg += '\nSpecial list for gRPC response with default value - empty or zero return (if has):'
        if recogParam.secure_context_level == 0:
            secureContextParamStr = '\nsecure_context_level: SUPPRESS'
            msg += secureContextParamStr
        if recogParam.result_format.format == 0:
            resultFormatStr = '\nresult_format { format: NLSML }'
            msg += resultFormatStr
        msg += '\n\nrecognition resource: \n' + str(recogRes)
        msg += '\nInput user_id: ' + str(user_id) + '\n'
        #
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)
        self.recognition_control_flag = False

        # call recognitionInit method ------
        self._recog_init_ = RecognitionInit(
            parameters=recogParam,
            resources=[recogRes],
            client_data=clientData,
            user_id = user_id
        )
        msg += 'recognition init: \n' + str(self._recog_init_)
        if self._logging_ > 1:
            print(msg)
        self._logger_.info(msg)
        #
        time.sleep(0.2)  # for debug
        return self._recog_init_

    # ------------------------------------
    # Define a function for recognition init with: RecognitionParameters & Repeated RecognitionResource (list)
    def recognition_init_repeated(self, recogParam=None, recogRes=None,
                                  clientData=None, user_id=None):  # note: recogRes -> iterable list
        # check & set default value -------
        if None == recogParam:
            recogParam = self.recognition_parameters()
        if None == recogRes:
            recogRes = [self.recognition_resource()]
        #
        msg = ''
        msg += 'recognition parameters: \n' + str(recogParam)
        msg += '\nSpecial list for gRPC response with default value - empty or zero return (if has):'
        if recogParam.secure_context_level == 0:
            secureContextParamStr = '\nsecure_context_level: SUPPRESS'
            msg += secureContextParamStr
        if recogParam.result_format.format == 0:
            resultFormatStr = '\nresult_format { format: NLSML }'
            msg += resultFormatStr
        msg += '\n\nrecognition resource: \n' + str(recogRes)
        msg += '\nInput user_id: ' + str(user_id) + '\n'
        #
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)
        self.recognition_control_flag = False    
        
        # call recognitionInit method ------
        self._recog_init_ = RecognitionInit(
            parameters=recogParam,
            resources=recogRes,
            client_data=clientData,
            user_id=user_id
        )
        msg += 'recognition init: \n' + str(self._recog_init_)
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)
        #
        time.sleep(0.2)  # for debug
        return self._recog_init_

    # Jyoti dtmf recognition init
    def dtmfrecognition_init(self, dtmfrecogParam=None,recogRes=None,clientData=None,user_id=None):  # note: only accept one recognition resource only here, for repeated recognition resource, see: recognition_init_repeated()
        # check & set default value -------
        if None == dtmfrecogParam:
            dtmfrecogParam = self.dtmfrecognition_parameters()
        if None == recogRes:
            recogRes = self.recognition_resource()
        #
        msg = ''
        msg += 'dtmfrecognition parameters: \n' + str(dtmfrecogParam)
        msg += '\nSpecial list for gRPC response with default value - empty or zero return (if has):'
        if dtmfrecogParam.secure_context_level == 0:
            secureContextParamStr = '\nsecure_context_level: SUPPRESS'
            msg += secureContextParamStr
        if dtmfrecogParam.result_format.format == 0:
            resultFormatStr = '\nresult_format { format: NLSML }'
            msg += resultFormatStr
        msg += '\n\nrecognition resource: \n' + str(recogRes)
        msg += '\nInput user_id: ' + str(user_id) + '\n'
        #
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)
        self.recognition_control_flag = False

        # call recognitionInit method ------
        self._dtmfrecog_init_ = DTMFRecognitionInit(
            parameters=dtmfrecogParam,
            resources=[recogRes],
            client_data=clientData,
            user_id=user_id
        )
        msg += 'recognition init: \n' + str(self._dtmfrecog_init_)
        if self._logging_ > 1:
            print(msg)
        self._logger_.info(msg)
        #
        time.sleep(0.2)  # for debug
        return self._dtmfrecog_init_
        
    # -----------------------------------------------
    # Define a function for client request stream - get stream request from a audio file
    @timeout(60)
    def client_stream(self, fileName=None, recInit=None):
        # check & set default value for testing purpose
        if None == fileName:
            fileName = self._audio_path_ + 'one.ulaw'
        if None == recInit:
            recInit = self.recognition_init()
        #
        msg = 'Client streaming: ... \n'
        msg += 'audio file: ' + fileName + '\n'
        msg += 'recognition init: \n' + str(recInit)
        #
        self._audioChunkSize_ = int(self._audioBufms_ * self._audioBytesPerMs_)  # gRPC Python client chunk
        msg += '\naudio stream chunk size: ' + str(self._audioChunkSize_) + '\naudio stream bytes per ms: ' + str(
            self._audioBytesPerMs_)
        msg += '\naudio stream buffer or interval ms: ' + str(self._audioBufms_)
        if self._logging_ > 1:
            print(msg)
        self._logger_.info(msg)
        time.sleep(0.5)
        rec_start_time = time.time()


        # gRPC client - RecognitionRequest - send audio stream request
        try:
            yield RecognitionRequest(recognition_init=recInit)
            #
            start_time = time.time()
            control_flag = True

            # check audio format then streaming send audio request
            # -------- PCM (or wav) -------------
            if self._audio_format_ == 'PCM':
                with wave.open(fileName) as wav:
                    msg = "\nTest audio total n frames: " + str(wav.getnframes())
                    # msg += "\nTest audio readframes sample: " + str(wav.readframes(2))
                    msg += "\nTest audio sample width: " + str(wav.getsampwidth())
                    msg += "\nTest audio frame rate: " + str(wav.getframerate())
                    if self._logging_ > 1:
                        print(msg)

                    # packet_samples = framerate * packet_duration
                    packet_samples = 8000 * self._audioBufms_ / 1000  # note: all audio frame rate = 8000 Hz
                    maxsize = 3000  # Hz, default -------
                    packet_num = 0
                    for packet in iter(lambda: wav.readframes(int(min(packet_samples, maxsize))), b''):
                        samples_sent = len(packet) / wav.getsampwidth()
                        effective_packet_duration = samples_sent / wav.getframerate()
                        # print('send (ms): ' + str(effective_packet_duration * 1000) + ' packet length: ' + str(len(
                        # packet)) + ' byte packet #' + str(packet_num + 1))
                        #
                        packet_num += 1
                        # correct streaming audio send drifting
                        now_time = time.time()
                        elapsed_ms = (now_time - start_time) * 1000
                        audioBuf_interval_sec = float(
                            max(0, int(self._audioBufms_ - elapsed_ms)) / 1000 / self._audioXrate_)
                        time.sleep(audioBuf_interval_sec)
                        start_time += (self._audioBufms_ / 1000)
                        #Start Control Message Code WAV
                        time_elapsed = (now_time - rec_start_time) * 1000
                        if self.recognition_control_flag:
                            if time_elapsed >= self.rec_control_time:
                                if control_flag:
                                    #
                                    msg = '\n*********** CONTROL SENT *********\n' + str(time_elapsed) + ' ms\n*********** ' 
                                    print(msg)
                                    yield RecognitionRequest(control=Control(start_timers=StartTimersControl()))
                                    control_flag = False

                        #End Control Message Code
                        msg = 'audio buffer interval second: ' + str(audioBuf_interval_sec) + '\n'
                        if not packet:
                            break
                        else:
                            packet_num += 1
                            dateTimeObj = datetime.now()
                            msg += 'Timestamp: ' + str(dateTimeObj) + ', audio interval(ms): ' + str(
                                self._audioBufms_) + ', audio packet: ' + str(packet_num) + ', length: ' + str(
                                len(packet))
                            if self._logging_ > 1:
                                print(msg)
                            self._logger_.info(msg)
                            yield RecognitionRequest(audio=bytes(packet))

            # -------- ULaw or ALaw ----------------------
            elif self._audio_format_ == 'ULaw' or self._audio_format_ == 'ALaw':
                #
                with open(fileName, 'rb') as f:
                    packet_num = 0
                    while True:
                        data = f.read(self._audioChunkSize_)  # set between 160 to thousands (default: 800, good: 2000)

                        # correct drifting
                        now_time = time.time()
                        elapsed_ms = (now_time - start_time) * 1000
                        audioBuf_interval_sec = float(
                            max(0, int(self._audioBufms_ - elapsed_ms)) / 1000 / self._audioXrate_)
                        time.sleep(audioBuf_interval_sec)
                        start_time += (self._audioBufms_ / 1000)
                        #Start Control Message Code ALAW / ULAW
                        time_elapsed = (now_time - rec_start_time) * 1000
                        if self.recognition_control_flag:
                            if time_elapsed >= self.rec_control_time:
                                if control_flag:
                                    #
                                    msg = '\n*********** CONTROL SENT *********\n' + str(time_elapsed) + ' ms\n*********** ' 
                                    print(msg)
                                    yield RecognitionRequest(control=Control(start_timers=StartTimersControl()))
                                    control_flag = False

                        #End Control Message Code
                        msg = 'audio buffer interval second: ' + str(audioBuf_interval_sec) + '\n'
                        if not data:
                            break
                        else:
                            packet_num += 1
                            dateTimeObj = datetime.now()
                            msg += 'Timestamp: ' + str(dateTimeObj) + ', audio interval(ms): ' + str(
                                self._audioBufms_) + ', audio packet: ' + str(packet_num) + ', length: ' + str(
                                len(data))
                            if self._logging_ > 1:
                                print(msg)
                            self._logger_.info(msg)
                            yield RecognitionRequest(audio=bytes(data))
            else:
                # pass
                raise Exception('Failed! NRC test with invalid audio format found. Quit \n')

        except Exception as e:
            msg = 'Error Found from client audio streaming! Exceptions detail: ' + repr(e)
            self._logger_.error(msg)
            if self._logging_ > 0:
                print(msg)
            self.cleanup()
        #


# Define a function for client request stream - get stream request from a audio file
    @timeout(60)
    def client_stream_dtmf(self, dtmfInput=None, dtmfrecInit=None):
        # check & set default value for testing purpose
        if None == dtmfInput:
            dtmfInput = "1234#5"
        if None == dtmfrecInit:
            dtmfrecInit = self.dtmfrecognition_init()
        
        msg = 'Client streaming: ... \n'
        msg += 'DTMF String: ' + dtmfInput + '\n'
        msg += 'recognition init: \n' + str(dtmfrecInit)
        
        #self._audioChunkSize_ = int(self._audioBufms_ * self._audioBytesPerMs_)  # gRPC Python client chunk
        #msg += '\naudio stream chunk size: ' + str(self._audioChunkSize_) + '\naudio stream bytes per ms: ' + str(self._audioBytesPerMs_)
        #msg += '\naudio stream buffer or interval ms: ' + str(self._audioBufms_)
        
        if self._logging_ > 1:
            print(msg)
        self._logger_.info(msg)
        
        time.sleep(0.5)
        
        rec_start_time = time.time()
        
        # gRPC client - DTMFRecognitionRequest - send dtmf stream request
        try:
            yield DTMFRecognitionRequest(recognition_init=dtmfrecInit)
            
            start_time = time.time()
            control_flag = True
            char_num = 0
            
            ## ---- Send all dtmf digits as 1 event
            # if self.recognition_control_flag:
            #    if time_elapsed >= self.rec_control_time:
            #        if control_flag:
            #                         #
            #            msg = '\n*********** CONTROL SENT *********\n' + str(time_elapsed) + ' ms\n*********** '
            #            print(msg)
            #            yield RecognitionRequest(control=Control(start_timers=StartTimersControl()))
            #            control_flag = False
            # yield DTMFRecognitionRequest(dtmf=dtmfInput)

            ## ---- Send 1 dtmf event at the time ---- ##
            for dtmfChar in dtmfInput:
                  now_time = time.time()
                  elapsed_time = (now_time - start_time)
                  start_time += elapsed_time
                  time_elapsed = (now_time - rec_start_time) * 1000

                  if self.recognition_control_flag:
                      if time_elapsed >= self.rec_control_time:
                          if control_flag:
                              #
                              msg = '\n*********** CONTROL SENT *********\n'# + str(time_elapsed) + ' ms\n*********** '
                              print(msg)
                              yield RecognitionRequest(control=Control(start_timers=StartTimersControl()))
                              control_flag = False

                  char_num += 1
                  dateTimeObj = datetime.now()
                  msg += 'Timestamp: ' + str(dateTimeObj) + ', interval(ms): ' + str(elapsed_time * 1000) + ', char_num: ' + str(char_num) + ', dtmfchar: ' + dtmfChar + '\n'
                  if self._logging_ > 1:
                      print(msg)
                  self._logger_.info(msg)
                  yield DTMFRecognitionRequest(dtmf=dtmfChar)
                  time.sleep(1)
          
        except Exception as e:
            msg = 'Error Found from client audio streaming! Exceptions detail: ' + repr(e)
            self._logger_.error(msg)
            if self._logging_ > 0:
                print(msg)
            self.cleanup()

    # --------------------------------------------------
    # Define a NRC gRPC service API call - Recognize - with a specific audio file as input
    @timeout(50)
    def clientRecognize(self, audiofile, recinit):
        # if None == channel:
        #    channel = grpc.insecure_channel(self._url_)
        #    self._channel_ = channel

        # check time elapsed for Recognize call
        start_time = time.time()
        msg = ''
        control_flag = True

        # Recognize call
        # --- handling test retry / re-run when connection failed ----
        retry_num = int(self._testRetryNum_)  # note: only retry for gRPC error or exception found;
        if retry_num < 1:
            retry_num = 1
        retry_sec = int(self._testRetryWait_)  # each retry wait for how many seconds
        if retry_sec < 1:
            retry_sec = 1
        for i in range(0, retry_num):
            try:
                if self.secure_connect:  # secure connection
                    channel = grpc.secure_channel(self._secure_url_, credentials=self._credentials_)
                    msg = '\nConnection via secure gRPC server: ' + self._secure_url_
                else:  # insecure connection
                    channel = grpc.insecure_channel(self._url_)
                    msg = '\nConnection via insecure gRPC server: ' + self._url_

                self._channel_ = channel
                stub = NRCStub(channel)

                msg += '\nClient Recognize... \n' + 'Channel: ' + str(channel)
                if self._logging_ > 0:
                    print(msg)
                self._logger_.info(msg)

                # Send metadata only if it is not empty
                if self._metadata_ != None: 
                    response_iterator = stub.Recognize(self.client_stream(fileName=audiofile, recInit=recinit), metadata=self._metadata_)
                else:
                    response_iterator = stub.Recognize(self.client_stream(fileName=audiofile, recInit=recinit))

                # Return response stream
                for response in response_iterator:
                    self._logger_.info(repr(response))
                    if self._logging_ > 1:
                        print('NRC recognize return: \n' + repr(response))  # for debug
                    yield response
                break

            except grpc.RpcError as e:
                e.details()
                status_code = e.code()
                msg += '\nError found on gRPC:\n' + 'status code:\n' + str(
                    status_code.name) + '\nstatus value:\n' + str(
                    status_code.value) + '\nstatus details:\n' + e.details()
                if status_code.name == 'UNAVAILABLE':
                    msg += '\n Retry QA test via gRPC, number: ' + str(i + 1) + '\n'
                    # self.cleanup()  # comment to avoid channel closed
                    time.sleep(retry_sec)
                    self._logger_.info(msg)
                    if self._logging_ > 0:
                        print(msg)
                    continue
                else:
                    self._logger_.error(msg)
                    if self._logging_ >= 0:
                        print(msg)

            except Exception as e:
                msg = '\nErrors or exceptions found!\n' + 'Exceptions details: ' + repr(e) + '\n'
                if self._logging_ >= 0:
                    print(msg)
                self._logger_.error(msg)
                # self.cleanup()

        # calculate time elapsed, unit: ms
        elapsed_time = int((time.time() - start_time) * 1000)  # convert to unit: ms
        msg = '\nTest NRC recognize call time elapsed: ' + str(elapsed_time) + '\n'
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)


    # Define a NRC gRPC service API call - DTMFRecognize - with a specific audio file as input
    @timeout(50)
    def clientDTMFRecognize(self, dtmfinput, dtmfrecinit):

        start_time = time.time()
        msg = ''
        control_flag = True

        # Recognize call
        # --- handling test retry / re-run when connection failed ----
        retry_num = int(self._testRetryNum_)  # note: only retry for gRPC error or exception found;
        
        if retry_num < 1:
            retry_num = 1
        retry_sec = int(self._testRetryWait_)  # each retry wait for how many seconds
        if retry_sec < 1:
            retry_sec = 1
        for i in range(0, retry_num):
            try:
                if self.secure_connect:  # secure connection
                    channel = grpc.secure_channel(self._secure_url_, credentials=self._credentials_)
                    msg = '\nConnection via secure gRPC server: ' + self._secure_url_
                else:  # insecure connection
                    channel = grpc.insecure_channel(self._url_)
                    msg = '\nConnection via insecure gRPC server: ' + self._url_

                self._channel_ = channel
                stub = NRCStub(channel)

                msg += '\nClient DTMFRecognize... \n' + 'Channel: ' + str(channel)
                if self._logging_ > 0:
                    print(msg)
                self._logger_.info(msg)
                
                # response_iterator = stub.DTMFRecognize(self.client_stream_dtmf(dtmfInput=dtmfinput, dtmfrecInit=dtmfrecinit))
                
                # Send metadata only if it is not empty
                if self._metadata_ != None: 
                    response_iterator = stub.DTMFRecognize(self.client_stream_dtmf(dtmfInput=dtmfinput, dtmfrecInit=dtmfrecinit), metadata=self._metadata_)
                else:
                    response_iterator = stub.DTMFRecognize(self.client_stream_dtmf(fdtmfInput=dtmfinput, dtmfrecInit=dtmfrecinit))
                
                # Return response stream
                for response in response_iterator:
                    self._logger_.info(repr(response))
                    if self._logging_ > 1:
                        print('NRC DTMF recognize return: \n' + repr(response))  # for debug
                    yield response
                break

            except grpc.RpcError as e:
                e.details()
                status_code = e.code()
                msg += '\nError found on gRPC:\n' + 'status code:\n' + str(
                    status_code.name) + '\nstatus value:\n' + str(
                    status_code.value) + '\nstatus details:\n' + e.details()
                if status_code.name == 'UNAVAILABLE':
                    msg += '\n Retry QA test via gRPC, number: ' + str(i + 1) + '\n'
                    # self.cleanup()  # comment to avoid channel closed
                    time.sleep(retry_sec)
                    self._logger_.info(msg)
                    if self._logging_ > 0:
                        print(msg)
                    continue
                else:
                    self._logger_.error(msg)
                    if self._logging_ >= 0:
                        print(msg)

            except Exception as e:
                msg = '\nErrors or exceptions found!\n' + 'Exceptions details: ' + repr(e) + '\n'
                if self._logging_ >= 0:
                    print(msg)
                self._logger_.error(msg)
                # self.cleanup()

        # calculate time elapsed, unit: ms
        elapsed_time = int((time.time() - start_time) * 1000)  # convert to unit: ms
        msg = '\nTest NRC recognize call time elapsed: ' + str(elapsed_time) + '\n'
        if self._logging_ > 0:
            print(msg)
        self._logger_.info(msg)


    # --------------------------------------------------------
    # Define a function for QA test case creation 2 - along final result also return special response message like StartOfSpeech & EndOfSpeech
    # def qa_nr_recognize_test_func2(self, channel=None, audioInput=None, recInit=None):
    def qa_nr_recognize_test_func1(self, audioInput=None, recInit=None):
        # check input
        # if None == channel:
        #   channel = self.connectgRPC()
        if None == audioInput:
            audioInput = 'one.ulaw'
        if None == recInit:
            recInit = self.recognition_init()

        # generate audio file path
        audioFile = self._audio_path_ + audioInput
        
        msg = 'QA NRC recognize test: ... \n'
        # msg += 'Test channel: ' + str(channel) + '\n'
        msg += 'Test audio file: ' + audioFile + '\n'
        # msg += 'Test recognition init: \n' + str(recInit) + '\n'
        self._logger_.info(msg)
        if self._logging_ > 0:
            print(msg)
        
        # Print metadata
        if self._metadata_ != None:
            msg = 'NRC QA test request metadata: ' + str(self._metadata_)
            print(msg)
            self._logger_.info(msg)

        # call recognize function
        resultIterator = self.clientRecognize(audiofile=audioFile, recinit=recInit)

        # get final recognize result
        status_code = None
        finalResult = None
        finalStartOfSpeechResult = None
        finalEndOfSpeechResult = None

        for recResult in resultIterator:
            # check status field
            if recResult.HasField('status'):
                status_code = recResult.status.code
                if status_code > 399:  # for negative case, server / client error
                    # if recResult.status.code == 400:
                    # raise Exception('Failed! NRC return ERROR with unexpected status code - Quit \n' + repr(recResult))
                    # break
                    finalResult = 'Failed! NRC return ERROR with unexpected status code - Quit \n' + str(
                        recResult.status)
                    print(finalResult)
                    break
            # check for special response field: start_of_speech and end_of_speech
            if recResult.HasField('start_of_speech'):
                if recResult.start_of_speech.first_audio_to_start_of_speech_ms == 0:  # note: gRPC zero is default for numerics in proto and empty are defaults for strings, for efficiency, default values are not transmitted across wire
                    finalStartOfSpeechResult = 'first_audio_to_start_of_speech_ms: ' + str(
                        recResult.start_of_speech.first_audio_to_start_of_speech_ms)
                else:
                    finalStartOfSpeechResult = str(recResult.start_of_speech)
            if recResult.HasField('end_of_speech'):
                if recResult.end_of_speech.first_audio_to_end_of_speech_ms == 0:  # note: gRPC zero is default for numerics in proto and empty are defaults for strings, for efficiency, default values are not transmitted across wire
                    finalEndOfSpeechResult = 'first_audio_to_end_of_speech_ms: ' + str(
                        recResult.end_of_speech.first_audio_to_end_of_speech_ms)
                else:
                    finalEndOfSpeechResult = str(recResult.end_of_speech)
            # check result field
            if recResult.HasField('result'):
                finalResult = recResult.result.formatted_text + recResult.result.status
                break
        #
        if status_code > 399:
            result_msg = finalResult
        else:
            result_msg = 'status code: ' + str(status_code) + '\n'
            result_msg += 'start_of_speech return: ' + str(finalStartOfSpeechResult) + '\n'
            result_msg += 'end_of_speech return: ' + str(finalEndOfSpeechResult) + '\n'
            result_msg += 'Final recognition result: \n' + str(finalResult) + '\n'
        self._logger_.info(result_msg)
        #
        return result_msg
    
    #Jyoti -- nrc dtmfrecognize client
    def qa_nr_dtmfrecognize_test_func1(self, dtmfInput=None, dtmfrecInit=None):

        if None == dtmfInput:
            dtmfInput = '1234#5'
        if None == dtmfrecInit:
            dtmfrecInit = self.dtmfrecognition_init()
        
        msg = 'QA NRC recognize test: ... \n'
        
        msg += 'Test dtmf String: ' + dtmfInput + '\n'
        msg += 'Test dtmfrecognition init: \n' + str(dtmfrecInit) + '\n'
        self._logger_.info(msg)
        if self._logging_ > 0:
            print(msg)
        
        # Print metadata
        if self._metadata_ != None:
            msg = 'NRC QA test request metadata: ' + str(self._metadata_)
            print(msg)
            self._logger_.info(msg)

        # call DTMFrecognize function
        resultIterator = self.clientDTMFRecognize(dtmfinput=dtmfInput, dtmfrecinit=dtmfrecInit)

        # get final recognize result
        status_code = None
        finalResult = None
        finalStartOfSpeechResult = None
        finalEndOfSpeechResult = None
        DTMF_rx=[]
        status_flag = True
        status_enabled = False

        for recResult in resultIterator:
            # check status field
            if recResult.HasField('status'):
                status_code = recResult.status.code
                if status_code > 399:  # for negative case, server / client error
                    finalResult = 'Failed! NRC return ERROR with unexpected status code - Quit \n' + str(
                        recResult.status)
                    print(finalResult)
                    break
                if((status_code==130) or (status_code==131)):
                    status_enabled = True
                    DTMF_rx.append(str(status_code))
                    for x in DTMF_rx:
                        n=len(DTMF_rx)
                        n1=sum("130" in s for s in DTMF_rx)
                        n2=sum("131" in s for s in DTMF_rx)
                        if("131" in x):
                            print("Total number of dtmf digits received is-----"+str(n))
                            if not ((n1==n-1)and(n2==1)and("131" in DTMF_rx[-1])):
                               status_flag = False 
            # check for special response field: start_of_speech and end_of_speech
            if recResult.HasField('start_of_speech'):
                if recResult.start_of_speech.first_audio_to_start_of_speech_ms == 0:  # note: gRPC zero is default for numerics in proto and empty are defaults for strings, for efficiency, default values are not transmitted across wire
                    finalStartOfSpeechResult = 'first_audio_to_start_of_speech_ms: ' + str(
                        recResult.start_of_speech.first_audio_to_start_of_speech_ms)
                else:
                    finalStartOfSpeechResult = str(recResult.start_of_speech)
            if recResult.HasField('end_of_speech'):
                if recResult.end_of_speech.first_audio_to_end_of_speech_ms == 0:  # note: gRPC zero is default for numerics in proto and empty are defaults for strings, for efficiency, default values are not transmitted across wire
                    finalEndOfSpeechResult = 'first_audio_to_end_of_speech_ms: ' + str(
                        recResult.end_of_speech.first_audio_to_end_of_speech_ms)
                else:
                    finalEndOfSpeechResult = str(recResult.end_of_speech)
            # check result field
            if recResult.HasField('result'):
                if ((status_enabled == True) and ("length=" in str(recResult))):
                    if ((status_flag == False) or ("131" not in DTMF_rx)):
                        time.sleep(5)
                        raise ValueError('Incorrect status messages for DTMF received')
                finalResult = recResult.result.formatted_text + recResult.result.status
                break
        
        if status_code > 399:
            result_msg = finalResult
        else:
            result_msg = 'status code: ' + str(status_code) + '\n'
            result_msg += 'start_of_speech return: ' + str(finalStartOfSpeechResult) + '\n'
            result_msg += 'end_of_speech return: ' + str(finalEndOfSpeechResult) + '\n'
            result_msg += 'Final recognition result: \n' + str(finalResult) + '\n'
        self._logger_.info(result_msg)
        
        return result_msg

    # Define a NRC gRPC service API call - Recognize - with a specific audio file as input
    def clientRecognizeNegativeTest(self, audiofile=None, recinit=None):
        # Recognize call
        msg = ''
        try:
            channel = grpc.insecure_channel(self._url_)
            self._channel_ = channel
            msg = '\nServer URL: ' + self._url_ + '\nChannel: ' + self._channel_
            if self._logging_ > 0:
                print(msg)
            self._logger_.info(msg)

            stub = NRCStub(channel)
            response_iterator = stub.Recognize(self.client_stream(fileName=audiofile, recInit=recinit))

            # Return response stream
            for response in response_iterator:
                # print('nrc.Recognize() --> ' + repr(response))  # for debug
                yield response

        except grpc.RpcError as e:
            e.details()
            status_code = e.code()
            msg = '\nError found on gRPC:\n' + 'status code:\n' + str(status_code.name) + '\nstatus value:\n' + str(
                status_code.value) + '\nstatus details:\n' + e.details()
            if self._logging_ > 0:
                print(msg)
            self._logger_.error(msg)

        except Exception as e:
            msg = '\nGeneral errors or exceptions found!\n' + 'Exceptions details: ' + repr(e) + '\n'
            if self._logging_ > 0:
                print(msg)
            self._logger_.error(msg)

    # ---------------------------------------------------
    # Define a function for NRC test result check
    @staticmethod
    def validateRecognitionResult(inputToCheck=None, expectResult=None):
        if None == inputToCheck:
            inputToCheck = ""
        if None == expectResult:
            expectResult = '<result>.+\/result>'
        #
        logger = logging.getLogger(__name__)
        msg = 'Test result to be checked: ' + str(inputToCheck)
        msg += 'Test validated expect result: ' + str(expectResult)
        logger.info(msg)
        if self._logging_ > 0:
            print(msg)
        # Validation
        pattern = re.compile(expectResult)
        ret = pattern.search(inputToCheck)
        #
        if ret:
            # check passed, return True
            msg = 'Test result validation... match ok!\n'
        else:
            # check failed, return False
            msg = 'Test result validation... match failed!\n'
        #
        logger.info(msg)
        if self._logging_ > 0:
            print(msg)
        return ret

    """"
    *************************************************
    Other functions
    
    *************************************************
    """

    def printMessagesList(self):
        i = 0
        for messages in self.messagesList:
            message = json.loads(messages)
            print('message ' + str(message))
            # print 'message ' + str(i) + ' is: ' + str(message['body'])
            i = i + 1

    def printErrorsList(self):
        i = 0
        for errors in self.errorsList:
            error = json.loads(errors)
            print('error:\n' + str(error))
            # print('message ' + str(i) + '\'s requestId is: ' + message)
            # print('error ' + str(i) + ' is: ' + str(error['body']))
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
        formattedTest = '\nTest Name: ' + testName + '\nLine Number: ' + str(
            lineNumber) + '\nLine Content: ' + lineContent + '\nStack Trace: ' + realStack
        return formattedTest


'''
    # --------------------------------------------------------
    # Define a function for QA test case
    # def qa_nr_recognize_test_func1(self, channel=None, audioInput=None, recInit=None):
    def qa_nr_recognize_test_func1(self, audioInput=None, recInit=None):
        # check input
        # if None == channel:
        #   channel = self.connectgRPC()
        if None == audioInput:
            audioInput = 'one.ulaw'
        if None == recInit:
            recInit = self.recognition_init()

        # generate audio file path
        audioFile = self._audio_path_ + audioInput
        #
        msg = 'QA NRC recognize test: ... \n'
        # msg += 'Test channel: ' + str(channel) + '\n'
        msg += 'Test audio file: ' + audioFile + '\n'
        msg += 'Test recognition init: \n' + str(recInit) + '\n'
        self._logger_.info(msg)
        if self._logging_ > 0:
            print(msg)

        # call recognize function
        # resultIterator = self.clientRecognize(channel=channel, audiofile=audioFile, recinit=recInit)
        resultIterator = self.clientRecognize(audiofile=audioFile, recinit=recInit)

        # get final recognize result
        finalResult = None
        for recResult in resultIterator:
            # check status field
            if recResult.HasField('status'):
                status_code = recResult.status.code
                if status_code > 399:  # for negative case, server / client error
                    # if recResult.status.code == 400:
                    # raise Exception('Failed! NRC return ERROR with unexpected status code - Quit \n' + repr(recResult))
                    # break
                    finalResult = 'Failed! NRC return ERROR with unexpected status code - Quit \n' + str(
                        recResult.status)
                    print(finalResult)
                    break
            # check result field
            if recResult.HasField('result'):
                finalResult = str(recResult.result)
                break
        #
        msg = 'Final recognition result: \n' + finalResult
        self._logger_.info(msg)
        #
        return finalResult

'''
