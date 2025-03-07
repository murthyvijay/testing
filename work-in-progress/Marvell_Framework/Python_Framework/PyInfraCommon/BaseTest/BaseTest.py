###################################################################################
#	Marvell GPL License
#	
#	If you received this File from Marvell, you may opt to use, redistribute and/or
#	modify this File in accordance with the terms and conditions of the General
#	Public License Version 2, June 1991 (the "GPL License"), a copy of which is
#	available along with the File in the license.txt file or by writing to the Free
#	Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 or
#	on the worldwide web at http://www.gnu.org/licenses/gpl.txt.
#	
#	THE FILE IS DISTRIBUTED AS-IS, WITHOUT WARRANTY OF ANY KIND, AND THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE ARE EXPRESSLY
#	DISCLAIMED.  The GPL License provides additional details about this warranty
#	disclaimer.
###################################################################################

from __future__ import print_function
from __future__ import absolute_import
# standard library imports
from builtins import str
from builtins import hex
from builtins import range
from builtins import object
import datetime
import argparse
import getpass
import inspect
import logging
import os, platform
import socket
import sys
import copy
import traceback
from collections import OrderedDict
from time import strftime, time

from ixexplorer.api.ixapi import IxTclHalError
from prettytable import PrettyTable, prettytable
# External Imports
from PyInfraCommon.BaseTest.BaseTestEnums.LogSeverityEnums import ReportFormat, ReportType
from PyInfraCommon.BaseTest.BaseTestStructures.BasetTestResources import TGConnectionsTable
from PyInfraCommon.ExternalImports.Communication import PySerialComWrapper, PyTelnetComWrapper, PySSHComWrapper, \
    PyBaseComWrapper
from PyInfraCommon.ExternalImports.ResourceManager import ResourceManager
from PyInfraCommon.ExternalImports.Logger import BaseTestLogger, LogType, GetLogger
from PyInfraCommon.ExternalImports.TG import *
from PyInfraCommon.GlobalFunctions.Serialize import JSONSerializable
from PyInfraCommon.GlobalFunctions.TG import TGPortListActions
from PyInfraCommon.GlobalFunctions.Utils.Exception import GetStackTraceOnException
from PyInfraCommon.GlobalFunctions.Utils.dict import RandomOrderedDict
from PyInfraCommon.Managers.SNMP.SNMPTools import SnmpManager, SnmpProtocolVersion
from PyInfraCommon.Managers.PowerDistributionUnit.PDUSocket import PduSocket_SNMP, PduSocket, USMAuthProtocol

# internal imports
from PyInfraCommon.BaseTest.BaseTestStructures.Types import TestDataCommon
from PyInfraCommon.BaseTest.BaseTestExceptions import TestFailedException, TestCrashedException
from PyInfraCommon.BaseTest.BaseTestStructures.BaseTestData import BaseTestData
from PyInfraCommon.GlobalFunctions.Utils.Function import GetFunctionName, getTimeStampStr, GetMainFileName, mswitch, \
    mcase
from PyInfraCommon.GlobalFunctions.Utils.Function import function_call_params
from PyInfraCommon.Globals.Logger.GlobalTestLogger import GlobalLogger
from PyInfraCommon.Managers.DataFileManager import DataFileManager
from PyInfraCommon.GlobalFunctions.Utils.Function import *
from .BaseTestEnums.TestReultTypeEnums import TestReultTypeEnums
from .BaseTestEnums.TestTypesEnums import TestTypesEnums, TestValidationGroup
from .BaseTestStructures.BasetTestResources import CommunicationSettings, MaxTcSettings, LinkPartnerTG

# from PyInfraCommon.Managers.MaxTcManager import MaxTC
from PyInfraCommon.BaseTest.BaseTestAbc import BaseTestAbc, abstractmethod
from PyInfraCommon.ExternalImports.EventManager import SysEventManager


class BaseTest(BaseTestAbc):
    """
    Base Test Class for all Base Test Types
    Each Specific BaseTest Type Should Inherit from it
    This Class only Defines the common Abstract methods of BaseTestAbc
    And thus each Specific Derived Test Class should implement the rest of the abstract methods:

    #Should Be Defined in Specific Base
    TestTearDown()
    DiscoverTestResources()
    #Should Be Defined in each Test Class (actual test)
    TestProcedure()

    :type TestData: BaseTestData
    :type logger: BaseTestLogger
    :type TGPorts: dict[int,PortClient]
    :type PDU: PduSocket
    :param _cleanup_stack: stack of functions to call to when running cleanup
    :type _cleanup_stack: list[PyInfraCommon.GlobalFunctions.Utils.Function.function_call_params]
    :param _cleanup_failure_stack: a stack of function callbacks that handles cleanup failutr
    :type _cleanup_failure_stack: list[PyInfraCommon.GlobalFunctions.Utils.Function.function_call_params]
    :param _debug_function_stack_per_step: stack of functions to call to when test has failed at some step
    :type _debug_function_stack_per_step: dict[int,list[PyInfraCommon.GlobalFunctions.Utils.Function.function_call_params]]
    :type _logger_manager: BaseTest._LoggerManager
    :type MaxTC:MaxTC
    """

    def __init__(self):
        self.TestData = BaseTestData()
        self.logger = None
        self._logger_manager = self._LoggerManager(self)
        self._report_manager = self._TestReportManager(self)
        self._SetTestType()
        self.TGManager = self._TGManager(self)
        self.TG = self.TGManager
        self.TGPorts = OrderedDict()
        self.LinkConnManager = self._LinkConnManager(self)
        self.TestSteps = self._TestStep(self)
        self.FileManager = DataFileManager()
        self.PDU = None
        self.MultiplePDU_dict = {}
        self.MaxTC = None
        self._cleanup_stack = []
        self._cleanup_failure_stack = []
        self._pre_test_callbacks_list = []
        self._post_test_callback_list = []
        self._debug_function_stack_per_step = OrderedDict()
        self.TGDutLinks = RandomOrderedDict()  # type: dict[int,BaseTest._TG2DutPortLink]
        self._args_parser = argparse.ArgumentParser(description="Command Line Option Parser for test scripts",
                                                    prefix_chars="-")
        self._args_object = None  # type: argparse.Namespace
        self._forced_setup_path = None
        self._forced_setup_list_path = None
        self._forced_setup_name = None
        self._launched_with_args = False
        self._printed_args = False
        self._InitArgParser()
        self.ConnectedToDutOnTestStart = True  # indicates whether to connect to Dut on test start or not
        self.SetupXlsPath = ""
        self._HandleCommandLineArgs()
        self.test_cli_args = ""

    def _InitArgParser(self, init_arg_object=True):
        """
        parse optional command line arguments passed to script
        :return:
        :rtype:
        """
        self._args_parser.add_argument("-s", "--setup_name", type=str,
                                       help="setup name to run this test on, will resolve the setup name from excel "
                                            "to a path to excel setup", required=False)
        self._args_parser.add_argument("-p", "--excel_setups_db_path", type=str,
                                       help="path to load the excel that contains"
                                            " the db with setups", required=False)
        self._args_parser.add_argument("-excel_path", "--excel_path", type=str,
                                       help="forces to take excel setup from this path", required=False)
        self._args_parser.add_argument("-test_args","--test_args",type=str,help="optional test args for any test",required=False)
        if init_arg_object:
            self._args_object = self._args_parser.parse_args()

    def _HandleCommandLineArgs(self, print_args=True):
        """
        handles passed command line args if passed
        :return:
        :rtype:
        """
        funcname = GetFunctionName(self._HandleCommandLineArgs)
        if hasattr(self._args_object, "excel_setups_db_path") and self._args_object.excel_setups_db_path is not None:
            self._forced_setup_list_path = self._args_object.excel_setups_db_path
            self._launched_with_args = True
        if hasattr(self._args_object, "setup_name") and self._args_object.setup_name is not None:
            self._forced_setup_name = self._args_object.setup_name
            self._launched_with_args = True
        if hasattr(self._args_object, "excel_path") and self._args_object.excel_path:
            self._forced_setup_path = self._args_object.excel_path
            self._launched_with_args = True
        if hasattr(self._args_object,"test_args") and self._args_object.test_args:
            self.test_cli_args = self._args_object.test_args
            self._launched_with_args = True

        if self._args_object and self._launched_with_args and print_args:
            # check if this was ovveriden
            if type(self)._HandleCommandLineArgs.__code__ is BaseTest._HandleCommandLineArgs.__code__:
                msg = funcname + "this test has been launched with the following input arguments:\n{}".format(
                    self._args_object)
                print(msg)

    def _BasicTestInit(self):
        """
        this method is called before the test is run by _TestInit() Method
        it should initialize any Basic test resource required by test e.g. TG, Log File,
        And perform any common pre test actions:
        e.g. create log file, connect to relevant Dut, connect to TG, etc.
        :return:
        """
        try:
            funcname = GetFunctionName(self._BasicTestInit)
            self.TestData.TestInfo._start_time_unit = datetime.datetime.now()
            self.TestData.TestInfo.start_time = self.TestData.TestInfo._start_time_unit.strftime("%H:%M:%S.%f")
            preprint = getTimeStampStr() + " " + funcname + ": "
            print(preprint + " Creating Log File...")
            self._logger_manager.InitTestLog()
            if self._args_object and self._launched_with_args:
                msg = funcname + "this test has been launched with the following input arguments:\n{}".format(
                    self._args_object)
                self.logger.trace(msg)
            msg = funcname + "this test is running from the following Setup Excel file {}".format(self.SetupXlsPath)
            self.logger.trace(msg)
            # Connect to TG If needed
            if self.TestData.TestInfo._UseTG:
                try:
                    self.TG.Connect()
                    self.LinkConnManager.UpdateTGPortInfo()
                except Exception as e:
                    self.FailTheTest(funcname + " Failed to Connect To TG:\n{}".format(e))
            count = 0
            channels_aquired = False
            for chanelName, channelval in list(self.TestData.Resources.Settings.CommunicationSetting.items()):
                if channelval.auto_connect_channel:
                    try:
                        if not channels_aquired:
                            self._GetDutChannels()
                            channels_aquired = True
                        count += 1
                        self.TestData.Resources.Settings.CommunicationSetting[chanelName] = CommunicationSettings(
                            self.TestData.Resources.Channels[chanelName])
                        if self.TestData.Resources.Channels[chanelName]:
                            # Provide test logger to Communication Channel
                            self.TestData.Resources.Channels[chanelName].testlogger = self.logger
                            if not self.TestData.Resources.Channels[chanelName].Connect():
                                return self.FailTheTest(funcname + "Failed to Connect To {}\n".format(chanelName))
                            if count == 1:
                                # save reference to first (main) dut channel in global info
                                from PyInfraCommon.Globals.DutChannel.DutMainChannel import GlobalDutChannel
                                GlobalDutChannel.channel = self.TestData.Resources.Channels[chanelName]
                    except Exception as e:
                        if self.TestData.Resources.Channels[chanelName]:
                            channel = self.TestData.Resources.Channels[chanelName]
                            if isinstance(channel, PySerialComWrapper):
                                if "access is denied" in str(e).lower():
                                    if hasattr(channel, "_port"):
                                        err = funcname + \
                                              """" Failed to Connect To COM{} port since the connection is 
                                              already opened. Please Disconnect your COM Port!!!\nOriginal Exception was: {}""".format(
                                                  channel._port, str(e))
                                        return self.FailTheTest(err)
                            elif isinstance(channel, PyTelnetComWrapper):
                                if hasattr(channel, "_host") and hasattr(channel, "_port"):
                                    err = funcname + """" Failed to open Telnet Connection to {} in TCP Port {}
                                    received the following error: {}""".format(channel._host, channel.__port, str(e))
                                    return self.FailTheTest(err)
                        return self.FailTheTest(funcname + "Failed to Connect To {}\n".format(chanelName) + str(e))
            # connect to PDU if needed
            if self.TestData.Resources.Settings.PduSettings.Connect_To_PDU:
                self.PDU = self._ConnectToPDU()
            self._ConnectToMultiplePDU()

            # connect to Max TC if needed
            if self.TestData.Resources.Settings.MaxTCSettings.auto_connect:
                self._ConnectToMaxTC()

        except Exception as e:
            if self.TestData.TestInfo._TestExceptionCaught and self.TestData.TestInfo._TestExceptionHandled:
                # Exception was already handled in previous stage raise it to calling moudle
                raise e
            else:
                return self._HandleException(e)

    def _GetDutChannels(self, path_to_setup=""):
        """
        Gets the Dut Channel from Resource Manager based on Excel Setup
        :return:
        :rtype:
        """
        count = 0
        funcname = GetFunctionName(self._GetDutChannels)
        for channelName, channelval in list(self.TestData.Resources.Settings.CommunicationSetting.items()):
            try:
                count += 1
                self.TestData.Resources.Channels[channelName] = ResourceManager.GetChannel(channelName=channelName,
                                                                                           connect=False,
                                                                                           current_config_file=path_to_setup)
                self.TestData.Resources.Channels[channelName].generate_uid = True # aLLow multiple connections to same host+ port
                self.TestData.Resources.Settings.CommunicationSetting[channelName] = CommunicationSettings(
                    self.TestData.Resources.Channels[channelName])
                if self.TestData.Resources.Channels[channelName]:
                    # Provide test logger to Communication Channel
                    self.TestData.Resources.Channels[channelName].testlogger = self.logger
            except Exception as e:
                err = funcname + "Caught Exception: {}".format(GetStackTraceOnException(e))
                return self.FailTheTest(err)

    def _ConnectToDutChannel(self, channel):
        """
        connects to dut channel and handles some exception
        :param channel: the dut channel
        :type channel: PyBaseComWrapper
        :return: True if Succeeded
        """
        funcname = GetFunctionName(self._ConnectToDutChannel)
        try:
            if self.ConnectedToDutOnTestStart:
                return channel.Connect()
        except Exception as e:
            err = ""
            if isinstance(channel, PySerialComWrapper):
                if "access is denied" in str(e).lower():
                    if hasattr(channel, "_port"):
                        err = funcname + "Failed to connect To COM{} port since the connection is already opened.\
                         Please Disconnect your COM Port!!!\nOriginal Exception was: {}".format(channel._port, e)
            elif isinstance(channel, PyTelnetComWrapper):
                if hasattr(channel, "_host") and hasattr(channel, "_port"):
                    err = funcname + "Failed to open Telnet Connection to {} in TCP Port {}\
                    received the following error: {}".format(channel._host, channel._port, e)
            elif isinstance(channel, PySSHComWrapper):
                if hasattr(channel, "_host") and hasattr(channel, "_port"):
                    err = funcname + "Failed to open SSH Connection to {} in TCP Port {}\
                    received the following error: {}".format(channel._host, channel._port, e)
            raise TestCrashedException(err)

    @classmethod
    def _InitSSHChannel(cls, host, user, password, timeout=None):
        """
        inits an ssh Channel
        :param host: ip address
        :type host: str
        :param user: user name
        :type user: str
        :param password: password
        :type password: str
        :return: PySSHComWrapper instance with all relevant params
        :rtype: PySSHComWrapper
        """

        class _connectionData(object):
            def __init__(self):
                self.ip_address = _connectionData.kv()
                self.port = _connectionData.kv()
                self.uname = _connectionData.kv()
                self.password = _connectionData.kv()

            class kv(object):
                def __init__(self):
                    self.key = ""
                    self.value = ""

        connectionData = _connectionData()
        connectionData.ip_address.value = host
        connectionData.port.value = 22
        connectionData.uname.value = user
        connectionData.password.value = password
        if timeout:
            setattr(connectionData, "timeout", _connectionData.kv())
            connectionData.timeout.value = timeout
        channel = PySSHComWrapper(connectionData)
        channel.testlogger = GlobalLogger.logger
        return channel

    @property
    def logger_manager(self):
        return self._logger_manager

    @abstractmethod
    def _SetTestType(self):
        """
        sets the test type and validation group client that uses this class
        :return:
        """
        pass

    def _ConnectToPDU(self, external_pdu_settings=None):
        """
        connects to a single PDU
        :param external_pdu_settings:optional input pdu settings
        :type external_pdu_settings:
        :return:
        :rtype:
        """
        funcname = GetFunctionName(self._ConnectToPDU)
        pdu_settings = external_pdu_settings
        PDU_Obj = None
        if external_pdu_settings is None:
            pdu_settings = self.TestData.Resources.Settings.PduSettings
        try:
            snmpobj = None
            version = pdu_settings._snmp_version
            ip = pdu_settings.ip_address
            community_read = "public"
            community_write = pdu_settings._community_rw
            outlet = pdu_settings.outlet
            auth_protocol_rw = pdu_settings._auth_protocol_rw
            password_rw = pdu_settings._password_rw
            privacy_protocol_rw = pdu_settings._privacy_protocol_rw
            username_rw = pdu_settings._username_rw
            while mswitch(version):
                if mcase(SnmpProtocolVersion.v2) or mcase(SnmpProtocolVersion.v1):
                    snmpobj = SnmpManager.get(version)
                    try:
                        snmpobj(ip, community_write, community_read)
                        PDU_Obj = PduSocket_SNMP(snmpobj, outlet)
                        PDU_Obj.Logger = self.logger
                    except Exception as e:
                        err = funcname + " failed to connect to PDU with the following settings:\
                        \nip:{}\tcommunity_read{}\tcommunity_write{}\toutlet{}\ngot error: {}".format(
                            ip, community_read, community_write, outlet, str(e))
                        self.logger.error(err)
                    break
                if mcase(SnmpProtocolVersion.v3):
                    try:
                        snmpobj = SnmpManager.get(version)
                        snmpobj.SetTrasnportLayerParams(ip)
                        snmpobj.SetSecurityData(username_rw, password_rw, None, auth_protocol_rw, privacy_protocol_rw)
                        PDU_Obj = PduSocket_SNMP(snmpobj, outlet)
                    except Exception as e:
                        err = funcname + " failed to connect to PDU with the following settings:\
                        \nip:{}\tusername_rw{}\tpassword_rw{}\tauth_protocol_rw{}\tprivacy_protocol_rw:{}\toutlet{}\n\
                        got error: {}" \
                            .format(ip, username_rw, password_rw, auth_protocol_rw, privacy_protocol_rw, outlet,
                                    str(e))
                        self.logger.error(e)
                if mcase("default"):
                    break
        except Exception as e:
            self.logger.error(
                funcname + "failed to init PDU, please check your excel setting and PDU device connectivity")
        finally:
            return PDU_Obj

    def _ConnectToMultiplePDU(self):
        """
        connects to multiple PDUs
        :return:
        :rtype:
        """
        for key,setting in self.TestData.Resources.Settings.MultiplePDUSettings.items():
            self.MultiplePDU_dict[key] = self._ConnectToPDU(external_pdu_settings=setting)




    def _ConnectToMaxTC(self, external_max_tc_settings=None):
        """
        :param external_max_tc_settings: ref to external max tc settings object
        :type external_max_tc_settings:
        :return: Max TC Object
        :rtype:MaxTC
        """
        funcname = GetFunctionName(self._ConnectToMaxTC)
        max_tc = None
        max_tc_settings = external_max_tc_settings
        if external_max_tc_settings is None:
            max_tc_settings = self.TestData.Resources.Settings.MaxTCSettings
        max_tc = MaxTC(device_id=max_tc_settings.device_id, ip_address=max_tc_settings.ip_address)
        if max_tc_settings.auto_connect:
            GlobalLogger.logger.debug(funcname + "connecting to MAX TC on ip {}".format(max_tc_settings.ip_address))
            res = max_tc.Connect()
            if not res:
                GlobalLogger.logger.error(funcname + "failed to connect")
            else:
                GlobalLogger.logger.debug(funcname + "Connection Successful")
        self.MaxTC = max_tc
        return max_tc

    @property
    def MaxTC(self):
        return self.TestData.Resources.MaxTC

    @MaxTC.setter
    def MaxTC(self, maxtc_obj):
        self.TestData.Resources.MaxTC = maxtc_obj

    @property
    def PDU(self):
        return self.TestData.Resources.PDU

    @PDU.setter
    def PDU(self, pduobj):
        self.TestData.Resources.PDU = pduobj

    @property
    def logger(self):
        # type: () -> BaseTestLogger
        if self.TestData.Resources.logger:
            return self.TestData.Resources.logger
        return None

    @logger.setter
    def logger(self, value):
        self.TestData.Resources.logger = value

    def _TestInit(self):
        """
        this method is called before the test is run,
        it Calls _BasicTestInit() and Test SpecificTestInit() methods:
        and thus perform full test init
        :return:
        """
        self.DiscoverTestResources()
        self._BasicTestInit()
        self.SpecificTestInit()
        resources_to_report = OrderedDict()
        resources_to_report["Dut Information"] = self.TestData.DutInfo
        for k, v in list(self.TestData.Resources.Settings.CommunicationSetting.items()):
            resources_to_report[k] = v.settings
        resources_to_report["PDU Settings"] = self.TestData.Resources.Settings.PduSettings
        if self.MultiplePDU_dict:
            resources_to_report["PDU Settings"] = self.TestData.Resources.Settings.MultiplePDUSettings
        resources_to_report["TG Connection Table"] = self.TestData.Resources.Settings.TG.ConnectionTable
        self._report_manager.Register_Resource(dictargs=resources_to_report)

    def TestPreRunConfig(self):
        """
        This method is called by the RunTheTests() method
        it is meant to _execute some initial pre-test configurations before actually running the tests
        if it is not necessary by derived class, then it can be just not implemented
        :return:
        """
        pass

    def RunTest(self):
        """
        Actual method which runs the test
        Calls TestPreRunConfig() to perform pre-test configurations
        And then TestProcedure() to _execute main test procedure
        :rtype: bool
        """
        try:
            self._TestInit()
            self._OnPreTest()
            self.TestPreRunConfig()
            self.InitTestStepsWithVars()
            self.logger.info(self.TestSteps, noFormat=True)
            self.TestProcedure()
            self._OnPostTest()
            self._OnTestEnd()
        except Exception as e:
            # Check if Exception was not already handled
            if not self.TestData.TestInfo._TestExceptionHandled:
                self._HandleException(e, False)
        finally:
            self._OnTestExit()
            return self.TestData.TestInfo._TestIntResult

    def InitTestStepsWithVars(self):
        """
        The methods initializes the TestSteps with dynamic variables (optional).
        Override this method in your test class, when you want to display dynamic information in test steps for user in
        the log file, otherwise leave it.
        """
        pass

    def FailTheTest(self, errmsg, abort_test=True):
        """
        this functions purpose is to mark test has failed
        :param errmsg: string of relevant error message describing failure reason and info
        :type errmsg: str
        :param abort_test: if True will abort test by raising exception, else will only mark that test had failed
        on this point
        :return:
        """
        funcname = GetFunctionName(self.FailTheTest)
        step_Err = errmsg
        self.TestData.TestInfo._TestIntResult = 0
        self.TestData.TestInfo._TestResultEnum = TestReultTypeEnums.tre_Failed
        short_step_err = ""
        if self.TestSteps.CurrentStep > 0:
            step_Err = "on Step {}:\n{}".format(self.TestSteps.CurrentStep, errmsg)
            short_step_err = "Failed On Step {} ".format(self.TestSteps.CurrentStep)

            if not not self.TestSteps.StepsStatus.steps:
                if self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration].get(self.TestSteps.CurrentStep):
                    step_info = self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][self.TestSteps.CurrentStep]
                    step_Err = "on Step {}: {}\nStep {} Description: {}". \
                        format(self.TestSteps.CurrentStep, errmsg, self.TestSteps.CurrentStep,
                               step_info.step_description)
                    short_step_err += "{}".format(step_info.step_description)
                self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][
                    self.TestSteps.CurrentStep].step_status = False
                if not self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][
                    self.TestSteps.CurrentStep].step_err_msg:
                    self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][
                        self.TestSteps.CurrentStep].step_err_msg = errmsg
                else:
                    # update the error message
                    self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][
                        self.TestSteps.CurrentStep].step_err_msg += "\n{}".format(errmsg)
            if self.logger:
                self.logger.error(step_Err)
            # run debug functions if needed
            try:
                self._RunDebugFunctionsForStep()
            except Exception as e:
                err = funcname + " test also failed to run debug functions per step {}: caught exception: {}". \
                    format(self.TestSteps.CurrentStep, GetStackTraceOnException(e))
                step_Err += "\n{}".format(err)
                self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][self.TestSteps.CurrentStep].step_err_msg += \
                    "\n{}".format(err)

        self.TestData.TestInfo.Result_Message = step_Err
        replace_chars = ["\n","\r",",","'",'"']
        for c in replace_chars:
            short_step_err = short_step_err.replace(c,"")
        self.TestData.TestInfo._Result_Short_Message += short_step_err
        if abort_test:
            if not self.TestData.TestInfo._TestExceptionCaught:
                raise TestFailedException(step_Err)

    def TestTearDown(self):
        """
        :return: cleanup function returned value or True if execution passed successfully
        :rtype: bool
        """
        funcname = GetFunctionName(self.TestTearDown)

        def Run_Cleanup_Recovery(test_class_ref):
            """
            :param test_class_ref:
            :type test_class_ref: BaseTest
            :return: True if succeeded, False otherwise
            :rtype: bool
            """

            local_funcname = GetFunctionName(test_class_ref.TestTearDown) + ":Run_Cleanup_Recovery"
            res = True
            if test_class_ref._cleanup_failure_stack:
                test_class_ref.logger.trace(local_funcname + "starting to call cleanup failure recovery function")
                while len(test_class_ref._cleanup_failure_stack):
                    try:
                        func_params = test_class_ref._cleanup_failure_stack.pop()
                        this_func_name = GetFunctionName(func_params.func)
                        # call the function
                        res &= func_params()
                        if res is not None and not res:
                            # we got a False return result from some cleanup function
                            err = funcname + " received {} result from cleanup failure recovery function {} !\n".format(
                                res, this_func_name)
                            test_class_ref.logger.error(err)
                            res = False
                    except Exception as e:
                        exp_info = "type {}, message {}".format(type(e), str(e))
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        teardown_err = "\nFull Exception Call Stack\n"
                        traceblist = traceback.format_exception(exc_type, exc_value, exc_traceback)
                        for tb in traceblist:
                            teardown_err += tb
                        exp_info += teardown_err
                        err = funcname + " caught exception from cleanup function {} cant continue, exception info:{}\n".format(
                            this_func_name, exp_info)
                        raise e.__class__(err)
                if not res:
                    raise TestCrashedException(funcname + " failed in the cleanup failure recovery process")
                return res

        result = True

        if self._cleanup_stack:
            # begin calling to cleanup functions
            self.logger.trace(funcname + " starting to call to cleanup functions of test")
            while len(self._cleanup_stack):
                func_params = self._cleanup_stack.pop()
                this_func_name = GetFunctionName(func_params.func)

                # call the function
                try:
                    res = func_params()
                    if res is not None and not res:
                        # we got a False return result from some cleanup function
                        err = funcname + " received {} result from cleanup function {} !\n".format(res, this_func_name)
                        self.logger.error(err)
                        result = False
                except Exception as e:
                    exc_data = GetStackTraceOnException(e)
                    err = funcname + " caught exception from cleanup function {}, exception info:{}\n".format(
                        this_func_name, exc_data)
                    # try to recover from cleanup failure
                    self.logger.error(err)
                    Run_Cleanup_Recovery(self)
                    raise e.__class__(err)
        if self.TGManager.is_connected:
            self.TG.Cleanup()

        if not result:
            Run_Cleanup_Recovery(self)
            raise TestFailedException(funcname + " cleanup process failed")

    def _DisconnectAllChannels(self):
        # disconnect all opened channels
        # for channel in self.TestData.Resources.Channels.values():
        try:
            PyBaseComWrapper.DisconnectAllChannels()
        except Exception as e:
            pass

    def _OnTestExit(self):
        """
        defines the routines to execute before test script exits
        this is the last point that occurs before test returns
        :return:
        :rtype:
        """
        funcname = GetFunctionName(self._OnTestExit)
        try:
            self._UpdateLastStepRunTime()
            self._UpdateTestRunTime()
            self._HandleTestResult()
            self._DisconnectAllChannels()
            env_report = self._report_manager.Build_Environment_Report()
            test_report = self._report_manager.Build_Test_Report()
            report = "{}\n{}".format(env_report, test_report)
            if self.logger is not None:
                self.logger.info(report)
            else:
                print(report)
            if self.TestData.TestInfo._TestIntResult != 1:
                err = "Test Failed!\n" * 10
                if self.logger is not None:
                    self.logger.error(err)
                else:
                    print(err)
            self._report_manager.Write_Test_Report()
            SysEventManager.UnRegisterAll()
        except Exception as ex:
            err = funcname + "caught exception outside of test: {}".format(GetStackTraceOnException(ex))
            self.logger.error(err)
            self.TestData.TestInfo._TestIntResult = 0
            err = "Test Failed!\n" * 10
            self.logger.error(err)
        try:
            self._logger_manager.CloseLogger()
        except Exception as ex1:
            self.TestData.TestInfo._TestIntResult = 0
            err = funcname + "caught exception While Closing Log file {}".format(GetStackTraceOnException(ex1))
            print(err)
            print(funcname + "generating temporary logfile with this error...")
            try:
                self.logger_manager.LogUnHandledExceptions(err)
            except Exception as ex2:
                err = funcname + "failed to open temp log file: {}".format(GetStackTraceOnException(ex2))
                print(err)

    def _OnTestEnd(self, test_result=None):
        self._UpdateLastStepRunTime()
        self.TestTearDown()
        self._UpdateTestRunTime()
        return self.TestData.TestInfo._TestIntResult

    def _OnTestCrash(self):
        """
        this method is called when a test crash, its checks if self._cleanup_crashed_tests_stack is not empty
        and start to pop and execute registered functions from the stack
        :return:
        :rtype:
        """
        funcname = GetFunctionName(self._OnTestCrash)
        result = True
        if self._cleanup_failure_stack:
            self.logger.trace(funcname + " starting to call test crashed registered functions...")
            err = ""
            while len(self._cleanup_failure_stack):
                func_params = self._cleanup_failure_stack.pop()
                this_func_name = GetFunctionName(func_params.func)
                # call the function
                try:

                    res = func_params()
                    if res is not None and not res:
                        # we got a False return result from some cleanup function
                        err = funcname + "received {} result from crashed tests handling function {} !\n".format(res,
                                                                                                                 this_func_name)
                        self.logger.error(err)
                        result = False
                except Exception as e:
                    exc_data = GetStackTraceOnException(e)
                    err += funcname + "caught exception from crashed tests handling function {}, exception info:{}\n".format(
                        this_func_name, exc_data)
                    # try to recover from cleanup failure
                    self.logger.error(err)
                    result = False
                finally:
                    if self.TGManager.is_connected:
                        self.TG.Cleanup()
                    if not result:
                        raise TestCrashedException(err)

    def _UpdateTestRunTime(self):

        if self.TestData.TestInfo._end_time_unit is None:
            self.TestData.TestInfo._end_time_unit = datetime.datetime.now()
        if not self.TestData.TestInfo.end_time:
            self.TestData.TestInfo.end_time = self.TestData.TestInfo._end_time_unit.strftime("%H:%M:%S.%f")
        if not self.TestData.TestInfo.run_time and self.TestData.TestInfo._start_time_unit is not None:
            run_time = self.TestData.TestInfo._end_time_unit - self.TestData.TestInfo._start_time_unit
            self.TestData.TestInfo.run_time = str(run_time)

    def _UpdateLastStepRunTime(self):
        if self.TestSteps.CurrentStep > 0:
            # update the last step run time
            step_info = self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][
                self.TestSteps.CurrentStep]  # type: BaseTest._TestStep._StepsInfo.StepInfo
            if step_info.step_end_time == 0.0:
                step_info.step_end_time = time()
                step_info.step_run_time = step_info.step_end_time - step_info.step_start_time
                self.TestSteps.StepsStatus.steps[self.TestSteps.Iteration][self.TestSteps.CurrentStep] = step_info

    def _HandleTestResult(self):
        """
        Handled the processing of tests results and actions needed per result
        :return:
        """
        logsufffix = ""
        # Test Ended Cleanly - Test Passed
        if self.TestData.TestInfo._TestResultEnum is None:
            self.TestData.TestInfo._TestResultEnum = TestReultTypeEnums.tre_Passed
            self.TestData.TestInfo._TestIntResult = 1
            self.TestData.TestInfo.Result = "Passed"
            logsufffix = "Passed"
        # there was exception on test
        else:
            # exception was from test
            if self.TestData.TestInfo._TestResultEnum is TestReultTypeEnums.tre_Failed:
                logsufffix = "Failed"
            elif self.TestData.TestInfo._TestResultEnum is TestReultTypeEnums.tre_FatalError:
                logsufffix = "Failed_FATAL_ERROR"
            # exception was not from the test --> test crashed
            elif self.TestData.TestInfo._TestResultEnum is TestReultTypeEnums.tre_Crashed:
                logsufffix = "Crashed"

            self.TestData.TestInfo.Result = logsufffix
        if self.logger is not None:
            if logsufffix == "Passed":
                self.logger.info("Test " + logsufffix)
                # test has failed
            else:
                self.logger.error("Test " + logsufffix + " " + self.TestData.TestInfo._Result_Message)
                self.logger.AppenSuffixToLogName(logsufffix)
        else:
            err = "Test " + logsufffix + " " + self.TestData.TestInfo._Result_Message
            print(err)

    def _RunDebugFunctionsForStep(self):
        """
        checks if that are debug functions that needs to be called for a given step and calls them
        :return:
        """
        local_funcname = GetFunctionName(self._RunDebugFunctionsForStep)
        step_stack = self._debug_function_stack_per_step.get(self.TestSteps.CurrentStep, None)
        res = True
        if step_stack:
            while len(step_stack):
                func_params = step_stack.pop()
                funcname = GetFunctionName(func_params.func)
                # call the function
                res &= func_params()
                if res is not None and not res:
                    err = local_funcname + "debug function {} for step {} failed".format(funcname,
                                                                                         self.TestSteps.CurrentStep)
                    self.logger.error(err)
        return res

    def _TestSummary(self):
        """
        This method is meant to be used whenever a test has finished
        either by existing normally or by failing
        is should generate a formatted summary file that describes various test info
        :return:
        """
        # TODO: Implement Full function
        self.TestData.TestInfo._end_time_unit = datetime.datetime.now()
        self.TestData.TestInfo.end_time = self.TestData.TestInfo._end_time_unit.strftime("%y-%m-%d-%H-%M")
        pass

    def _HandleException(self, e, raise_excpetion=True):
        # type: (Exception) -> int
        """
        Exception Handler, handles all exception types
        :param e:  exception object
        :param raise_excpetion: if True will raise back the exception after handling it, else will return False
        :type e: Exception
        :type raise_excpetion: bool
        :return: int
        :rtype: int

        """
        funcname = GetFunctionName(self._HandleException)

        if isinstance(e, TestFailedException):
            # Test Has Failed, Check if Failed Info was already set
            self.TestData.TestInfo.Result_Message = str(e)
            if self.TestData.TestInfo._TestIntResult is None:
                self.TestData.TestInfo._TestIntResult = 0
            if not self.TestData.TestInfo._TestResultEnum:
                self.TestData.TestInfo._TestResultEnum = TestReultTypeEnums.tre_Failed
        # TODO: handle specific system exceptions
        elif isinstance(e, Exception):
            # Get Traceback
            teardown_err = GetStackTraceOnException(e)
            self.TestData.TestInfo._Result_Message += teardown_err
            replace_chars = ["\n","\r",",","'",'"']
            short_err = str(e)
            for c in replace_chars:
                short_err = short_err.replace(c,"")

            self.TestData.TestInfo._Result_Short_Message += short_err
            self.TestData.TestInfo._Result_Short_Message_Type = "CRASH"
            if not self.TestData.TestInfo._TestIntResult:
                self.TestData.TestInfo._TestIntResult = 0
            if not self.TestData.TestInfo._TestResultEnum:
                self.TestData.TestInfo._TestResultEnum = TestReultTypeEnums.tre_Crashed
            # handle the crash
            self.logger.error(funcname + "######### Test Crashed!! ##########\n{}".format(teardown_err))
            self._OnTestCrash()

        # Run test teardown if possible
        try:
            if self.TestData.TestInfo._TestResultEnum is not TestReultTypeEnums.tre_Crashed:
                self.TestTearDown()
        except Exception as ex:
            self.TestData.TestInfo._Result_Message += """
        Test also Crashed in the TearDown Process with the following exception:\n{}""".format(str(ex))
            self.TestData.TestInfo._TestResultEnum = TestReultTypeEnums.tre_Crashed
        # mark the testException Info as Handled and log all the exception info
        self.TestData.TestInfo._TestExceptionCaught = True
        self.TestData.TestInfo._TestExceptionHandled = True
        self.TestData.TestInfo._TestExceptionObj = e
        # Handle Test Result
        self._HandleTestResult()
        # Raise the exception onwards so it will be captured by the running process
        if raise_excpetion:
            raise e
        else:
            return self.TestData.TestInfo._TestIntResult

    def Add_Cleanup_Function_To_Stack(self, func, *args, **kwargs):
        """
        adds functions to stack of functions to call to on cleanup stage
        on TestTearDown()
        :param func:  function to call to
        :param args: optional args to use when calling function
        :param kwargs: optional kwargs to use when calling function
        :return:None
        """
        funcname = GetFunctionName(self.Add_Cleanup_Function_To_Stack)
        func_params = function_call_params()
        func_params.valditate_params(funcname, func, args, kwargs)
        func_params.func = func
        if args:
            func_params.args = args
        if kwargs:
            func_params.kwargs = kwargs

        # if reboot was requested clear the stack and only push this function
        this_func_name = GetFunctionName(func_params.func)
        if 'CpssDutManager::reboot:' in this_func_name or 'RebootDut' in this_func_name:
            self._cleanup_stack = []
        # push to stack
        self._cleanup_stack.append(func_params)

    def Add_Debug_Function_To_Stack_Per_Step(self, step_num, func, *args, **kwargs):
        """
       adds debug functions to stack of functions that will be called when a test has failed on some step
       on TestTearDown()
       :param step_num: step number
       :type step_num:int
       :param func:  function to call to per given step
       :param args: optional args to use when calling function
       :param kwargs: optional kwargs to use when calling function
       :return:None
       """
        funcname = GetFunctionName(self.Add_Debug_Function_To_Stack_Per_Step)
        func_params = function_call_params()
        func_params.valditate_params(funcname, func, args, kwargs)
        func_params.func = func
        if args:
            func_params.args = args
        if kwargs:
            func_params.kwargs = kwargs
        # push to stack
        if self._debug_function_stack_per_step.get(step_num, None):
            # already have existing stack for this step
            self._debug_function_stack_per_step[step_num].append(func_params)
        else:
            # create new stack for this step
            self._debug_function_stack_per_step[step_num] = [func_params]

    def _AddCleanupRecoveryCrashHandler(self, func, *args, **kwargs):
        """
        adds functions to stack of functions to be called if TestTearDown failes or crashes
        :param func:  function to call to
        :param args: optional args to use when calling function
        :param kwargs: optional kwargs to use when calling function
        :return:None
        """
        funcname = GetFunctionName(self._AddCleanupRecoveryCrashHandler)
        func_params = function_call_params()
        func_params.valditate_params(funcname, func, args, kwargs)
        func_params.func = func
        if args:
            func_params.args = args
        if kwargs:
            func_params.kwargs = kwargs
        # push to stack
        self._cleanup_failure_stack.append(func_params)

    def Add_Pre_Test_Functions(self, func, *args, **kwargs):
        """
        registers test functions to run after test init and before TestPreRunConfig + TestProceudre
        :param func:  function to call to
        :param args: optional args to use when calling function
        :param kwargs: optional kwargs to use when calling function
        :return:None
        """
        funcname = GetFunctionName(self.Add_Pre_Test_Functions)
        func_params = function_call_params()
        func_params.valditate_params(funcname,func,args,kwargs)
        func_params.func=func
        if args:
            func_params.args = args
        if kwargs:
            func_params.kwargs = kwargs

        # if reboot was requested clear the stack and only push this function
        this_func_name = GetFunctionName(func_params.func)
        # append to cb list
        self._pre_test_callbacks_list.append(func_params)

    def Add_Post_Test_Functions(self, func, *args, **kwargs):
        """
        registers test functions to run after test finished and before cleanup
        :param func:  function to call to
        :param args: optional args to use when calling function
        :param kwargs: optional kwargs to use when calling function
        :return:None
        """
        funcname = GetFunctionName(self.Add_Post_Test_Functions)
        func_params = function_call_params()
        func_params.valditate_params(funcname,func,args,kwargs)
        func_params.func=func
        if args:
            func_params.args = args
        if kwargs:
            func_params.kwargs = kwargs

        # if reboot was requested clear the stack and only push this function
        this_func_name = GetFunctionName(func_params.func)
        # append to cb list
        self._post_test_callback_list.append(func_params)

    def _OnPreTest(self):
        """
        runs all callbacks from pre_test stack if stack not empty
        :return:
        :rtype:
        """
        funcname = GetFunctionName(self._OnPreTest)
        if self._pre_test_callbacks_list:
            # begin calling to cleanup functions
            self.logger.trace(funcname + " starting to run registered pre test functions")

            for cb in self._pre_test_callbacks_list:
                this_func_name = GetFunctionName(cb.func)

                # call the function
                try:
                    res = cb()
                    if res is not None and not res:
                        # we got a False return result from some cleanup function
                        err = funcname + " received {} result from pre test function {}!".format(res, this_func_name)
                        self.logger.error(err)
                        result = False
                except Exception as e:
                    exc_data = GetStackTraceOnException(e)
                    err = funcname + " caught exception from pre test function {}:{}".format(
                        this_func_name, exc_data)
                    self.logger.error(err)
                    raise e

    def _OnPostTest(self):
        """
        runs all callbacks from pre_test stack if stack not empty
        :return:
        :rtype:
        """
        funcname = GetFunctionName(self._OnPostTest)
        if self._post_test_callback_list:
            # begin calling to cleanup functions
            self.logger.trace(funcname + " starting to run registered post test functions")

            for cb in self._post_test_callback_list:
                this_func_name = GetFunctionName(cb.func)
                # call the function
                try:
                    res = cb()
                    if res is not None and not res:
                        # we got a False return result from some cleanup function
                        err = funcname + " received {} result from post test function {}!".format(res, this_func_name)
                        self.logger.error(err)
                        result = False
                except Exception as e:
                    exc_data = GetStackTraceOnException(e)
                    err = funcname + " caught exception from post test function {}:{}".format(
                        this_func_name, exc_data)
                    self.logger.error(err)
                    raise e


    class _TestStep(BaseTestAbc.TestStepsABC):

        def __init__(self, test_class_ref=None):
            self._steps = {}  # type: OrderedDict(int,str)
            self.logger = None  # type: BaseTestLogger
            self.CurrentStep = 0
            self.StepsHistory = []  # indicator list to know if we already ran a step before
            self.Iteration = 0  # if running steps in loop then need to update this
            self.TestDescription = BaseTest._TestStep._TestDescription()
            self.StepsStatus = self._StepsInfo()
            self._test_class_ref = test_class_ref  # type: BaseTest

        @property
        def Step(self):
            return self._steps

        def RunStep(self, step, step_iteration_info=""):
            """
            this method indicates the last step executed in the test
            it also logs the current step to the test log
            :param step: the step number you are running
            :type step:int
            :param step_iteration_info: additional info about your step, relevant if running the step in a loop
            and you want to provide specific info about the current iteration
            :type step_iteration_info: str
            :return:
            """
            err = False
            new_iteration = False
            funcname = GetFunctionName(self.RunStep)
            errmsg = funcname + ": "
            # validate step type
            errmsg += "step variable must be of type int or str with digits only "
            if type(step) == str:
                if not step.isdigit():
                    err = True
                else:
                    step = int(step)
            elif type(step) != int:
                err = True
            elif not self.Step.get(step, None):
                err = True
                errmsg += "step " + str(step) + " does not exist on steps dictionary" + str(self.Step)
            if not err:
                self.CurrentStep = step
                step_info = self.StepsStatus.GetInstance()  # type: BaseTest._TestStep._StepsInfo.StepInfo
                step_info.step_num = step
                step_info.step_description = "[{}] ".format(step_iteration_info) if step_iteration_info else ""
                step_info.step_description += self.Step[step]
                step_info.step_iteration_info = step_iteration_info
                step_info.step_start_time = time()
                # check iteration
                if step in self.StepsHistory:
                    # we have a a repeated step
                    self.Iteration += 1
                    self.StepsHistory = []
                    new_iteration = True
                step_info.step_iteration_num = self.Iteration
                if not len(self.StepsStatus.steps):
                    # first creation
                    od = OrderedDict()
                    od[step] = step_info
                    self.StepsStatus.steps = [od]
                elif new_iteration:
                    od = OrderedDict()
                    od[step] = step_info
                    self.StepsStatus.steps.append(od)
                else:
                    self.StepsStatus.steps[self.Iteration][step] = step_info
                previous_Step = step - 1
                if previous_Step > 0 and self.StepsStatus.steps[self.Iteration] and \
                        self.StepsStatus.steps[self.Iteration].get(previous_Step):
                    # if this is not the first step or not the first Iteration then update end time of previous step
                    prev = self.StepsStatus.steps[self.Iteration][
                        previous_Step]  # type: BaseTest._TestStep._StepsInfo.StepInfo
                    prev.step_end_time = time()
                    prev.step_run_time = prev.step_end_time - prev.step_start_time
                    self.StepsStatus.steps[self.Iteration][previous_Step] = prev
                if previous_Step == 0 and self.Iteration > 0:
                    k, prev = self.StepsStatus.steps[self.Iteration - 1].popitem(last=True)
                    prev.step_end_time = time()
                    prev.step_run_time = prev.step_end_time - prev.step_start_time
                    self.StepsStatus.steps[self.Iteration - 1][k] = prev
                self.StepsHistory.append(step)

                if self.logger:
                    self.logger.info("Executing step {}: {}".format(step, step_info.step_description))
            else:
                raise TestCrashedException(errmsg)

        def __str__(self):
            # print test description and steps if exists
            ret = ""
            test_name = self._test_class_ref.TestData.TestInfo.Test_Name
            suite_name = self._test_class_ref.TestData.TestInfo.Suite_Name
            cols = ["Suite Name", "Test Name", "Purpose", "Author", "Test Document Reference"]
            if self.TestDescription is not None:
                pretty_table = PrettyTable()
                purpose = self.TestDescription.test_purpose
                author = self.TestDescription.test_author
                reference = self.TestDescription.test_case_reference
                row = [suite_name, test_name, purpose, author, reference]
                pretty_table.field_names = cols
                pretty_table.align ="l"
                pretty_table.valign = "t"
                pretty_table.add_row(row)
                pretty_table.title = "Test Description"
                pretty_table.max_width = 70
                pretty_table.hrules = prettytable.ALL
                ret += pretty_table.get_string()

            pretty_table = PrettyTable()

            # ret += "######### Test Procedure #########\n"

            if len(self._steps) > 0:
                cols = ["Step", "Step Description"]
                pretty_table.field_names = cols
                pretty_table.title = "Test Procedure"
                for step, stepstr in list(self._steps.items()):
                    # ret += "Step " + str(step) + ": " + stepstr +"\n"
                    pretty_table.add_row([str(step), stepstr])
                pretty_table.max_width = 70
                pretty_table.hrules = prettytable.ALL
                pretty_table.align ="l"
                pretty_table.valign = "t"
                ret += "\n\n{}".format(pretty_table.get_string())
            return ret

        class _StepsInfo(object):
            """
            internal class that holds step status and other info
            :type steps: list[OrderedDict[int,BaseTest._TestStep._StepsInfo.StepInfo]]
            """

            def __init__(self):
                self.steps = []
                self.pretty_table = None  # type: PrettyTable
                self.errors_pretty_table = None
                self.has_failures = False

            def __str__(self):
                ret = ""
                if not self.pretty_table:
                    self.Gen_Pretty_Table()
                ret = self.pretty_table.get_string()
                if self.has_failures:
                    self.Gen_Errors_Pretty_Table()
                    ret += "\n\n{}".format(self.errors_pretty_table.get_string())
                return ret

            def To_HTML_Table(self):
                """
                generate self attributes representation in HTML Table format
                :return: HTML string of a table of self attributes
                :rtype: str
                """
                ret = ""
                if not self.pretty_table:
                    self.Gen_Pretty_Table()
                ret = self.pretty_table.get_html_string()
                return ret

            def Gen_Pretty_Table(self):
                self.pretty_table = PrettyTable()
                self.pretty_table.title = "Test Steps Summary"
                self.pretty_table.hrules = prettytable.ALL
                has_iterations = False
                if len(self.steps):
                    if len(self.steps) == 1:
                        cols = ["Step", "Description", "Result", "Run Time"]
                    else:
                        cols = ["Step", "Iteration", "Iteration Info", "Description", "Result", "Run Time"]
                        has_iterations = True
                    self.pretty_table.field_names = cols
                    self.pretty_table.align = "l"
                    self.pretty_table.valign = "t"
                    self.pretty_table.max_width = 100
                    self.pretty_table.hrules = prettytable.ALL
                    for steps in self.steps:
                        for id, step in list(steps.items()):  # type: BaseTest._TestStep._StepsInfo.StepInfo
                            self.pretty_table.add_row(step.To_Str_List(has_iterations))
                            if not step.step_status:
                                self.has_failures = True

            def Gen_Errors_Pretty_Table(self):
                self.errors_pretty_table = PrettyTable()
                self.errors_pretty_table.title = "Steps Failure Summary"
                self.errors_pretty_table.hrules = prettytable.ALL
                has_iterations = False
                if len(self.steps):
                    if len(self.steps) == 1:
                        cols = ["Step", "Error"]
                    else:
                        cols = ["Step", "Iteration", "Iteration Info", "Error"]
                        has_iterations = True
                    self.errors_pretty_table.field_names = cols
                    self.errors_pretty_table.align = "l"
                    # self.errors_pretty_table.max_width = 75
                    self.errors_pretty_table.hrules = prettytable.ALL
                    for steps in self.steps:
                        for id, step in list(steps.items()):  # type: BaseTest._TestStep._StepsInfo.StepInfo
                            if not step.step_status:
                                self.has_failures = True
                                self.errors_pretty_table.add_row(step.To_Err_Str_List(has_iterations))

            @classmethod
            def GetInstance(cls):
                # type: () -> BaseTest._TestStep._StepsInfo.StepInfo
                return cls.StepInfo()

            class StepInfo(object):
                """
                internal class that holds test step status and other info
                """

                def __init__(self, num=0, status=True, description="", err_msg=""):
                    self.step_num = num
                    self.step_status = status
                    self.step_iteration_info = ""
                    self.step_iteration_num = 0
                    self.step_description = description
                    self.step_err_msg = err_msg
                    self.step_run_time = 0.0
                    self.step_start_time = 0.0
                    self.step_end_time = 0.0

                def To_Str_List(self, withIterationIfno=False):
                    """

                    :param withIterationIfno: indicate if to include iteration info
                    :type withIterationIfno: bool
                    :return:self class as list of strings
                    :rtype: list[str]
                    """
                    ret = [str(self.step_num)]
                    if withIterationIfno:
                        ret.append(self.step_iteration_num)
                        ret.append(self.step_iteration_info)
                    ret.append(self.step_description)
                    res = "Passed" if self.step_status else "Failed"
                    ret.append(res)
                    # ret.append(self.step_err_msg)
                    ret.append(self.step_run_time)
                    return ret

                def To_Err_Str_List(self, withIterationIfno=False):
                    """
                    :param withIterationIfno:indicate if to include iteration info
                    :type withIterationIfno:bool
                    :return:self class error info as list of strings
                    :rtype:str
                    """
                    ret = [str(self.step_num)]
                    if withIterationIfno:
                        ret.append(self.step_iteration_num)
                        ret.append(self.step_iteration_info)
                    ret.append(self.step_err_msg)
                    return ret

        class _TestDescription(object):
            def __init__(self):
                self.test_author = ""
                self.test_case_reference = ""
                self.test_purpose = ""

    class _LoggerManager(object):
        """
        internal class that manages the test logger
        :type test_data_ref: BaseTestData
        :type self.test_class_ref: BaseTest
        """

        def __init__(self, test_class_ref):
            """

            :param test_class_ref: reference to test class
            :type test_class_ref: BaseTest
            """
            self.log_created = False
            self.log_creation_date = ""
            self.log_dir_path = ""
            self.log_GRASS_base_path = ""
            self.file_name = ""
            self.orig_file_name = ""
            self.log_format = LogType.HTML_LOGGER
            self.log_level = None
            self.test_class_ref = test_class_ref
            self.test_data_ref = self.test_class_ref.TestData
            self._logger_callbacks = []

        def InitTestLog(self):
            """
            generates the test log for the test
            :return:
            """
            funcname = GetFunctionName(self.InitTestLog)
            self.InitLogFilename()
            # update test name based on file name
            self.log_format = LogType.HTML_LOGGER
            self.BuildLogPath()
            if self.test_data_ref.Resources.Settings.LogSettings.logging_format:
                if "html" in self.test_data_ref.Resources.Settings.LogSettings.logging_format.lower():
                    self.log_format = LogType.HTML_LOGGER
                elif "text" in self.test_data_ref.Resources.Settings.LogSettings.logging_format.lower():
                    self.log_format = LogType.TEST_LOGGER
            tmp_timestamp = datetime.datetime.now().strftime('_%H-%M-%S-%f')
            self.test_class_ref.logger = GetLogger(self.test_data_ref.TestInfo.Test_Name + tmp_timestamp,
                                                   self.log_dir_path, self.test_data_ref.TestInfo.Test_Name,
                                                   append_source_name=False, logger_type=self.log_format)
            for cb in self._logger_callbacks:
                # add logger cb if existing
                self.test_class_ref.logger.addLoggingCallBack(cb)

            if self.test_class_ref.logger:
                self.log_created = True
            if self.test_data_ref.Resources.Settings.LogSettings.logging_level:
                level = self.test_data_ref.Resources.Settings.LogSettings.logging_level
                level = level.upper().strip()
                self.test_class_ref.logger.setLoggingLevel(level)
                self.log_level = level
            # update the singletone logger module
            if GlobalLogger._logger is not None:
                del GlobalLogger._logger
            GlobalLogger.logger = self.test_class_ref.logger
            self.test_class_ref.TestSteps.logger = self.test_class_ref.logger
            self.test_class_ref.TG.logger = self.test_class_ref.logger

        def Addlogger_callback(self, cb):
            """
            adds callback logger function to logger upon init
            :param cb:
            :type cb:
            :return:
            :rtype:
            """
            self._logger_callbacks.append(cb)

        def InitLogFilename(self):
            self.file_name = filename = GetMainFileName()
            self.file_name = filename
            self.orig_file_name = self.file_name
            # for CV also ADD the ASICType-BoardType to Filename
            if self.test_data_ref.TestInfo._TestValidationGroup == TestValidationGroup.CV:
                ASIC_Name = self.test_data_ref.DutInfo.ASIC
                if self.test_data_ref.DutInfo.Board_Model:
                    ASIC_Name += "-" + self.test_data_ref.DutInfo.Board_Model
                if self.test_data_ref.DutInfo.CPU_CoreClock:
                    ASIC_Name += "-{}".format(self.test_data_ref.DutInfo.CPU_CoreClock)
                self.file_name += "_" + ASIC_Name
            self.test_data_ref.TestInfo.Test_Name = self.file_name

        def BuildLogPath(self, path_dir_list=None):
            funcname = GetFunctionName(self.BuildLogPath)
            if not self.log_GRASS_base_path:
                currentDir = os.getcwd()
                self.log_GRASS_base_path = os.path.join(currentDir, "Results", self.orig_file_name, '')
            if not self.log_creation_date:
                self.log_creation_date = strftime('%d-%m-%Y')
            path = self.log_GRASS_base_path
            if not path_dir_list:
                ASIC_Name = self.test_data_ref.DutInfo.ASIC
                if self.test_data_ref.DutInfo.Board_Model:
                    ASIC_Name += "-" + self.test_data_ref.DutInfo.Board_Model
                if self.test_data_ref.DutInfo.CPU_CoreClock:
                    ASIC_Name += "-{}".format(self.test_data_ref.DutInfo.CPU_CoreClock)
                path_dir_list = [self.test_data_ref.DutInfo._Customer_Name, self.test_data_ref.DutInfo._Project,
                                 ASIC_Name, self.test_data_ref.DutInfo.Software_Version,
                                 self.test_data_ref.TestInfo.Suite_Name,
                                 self.log_creation_date, self.orig_file_name]
            for i in range(len(path_dir_list)):
                Dir = path_dir_list[i]
                if Dir != "":
                    if i != len(path_dir_list) - 1:
                        path = os.path.join(path, Dir, '')
                    else:
                        path = os.path.join(path, Dir)
            self.log_dir_path = path

        def ChangeLogPath(self, path_dir_list=None):
            """
            changes the logger logfile path, if path not given builds path from test_data_ref.DutInfo
            :param path_dir_list: list of directories that form a path
            :type path_dir_list:list
            :return:
            """
            old_path = self.log_dir_path
            self.InitLogFilename()
            self.BuildLogPath(path_dir_list)
            self.test_class_ref.logger.rename_logger(self.log_dir_path, self.file_name)
            # update the singletone logger module
            GlobalLogger.logger = self.test_class_ref.logger
            self.test_class_ref.TestSteps.logger = self.test_class_ref.logger
            # remove the old path
            try:
                os.removedirs(old_path)
            except OSError:
                pass

        def CloseLogger(self):
            funcname = GetFunctionName(self.CloseLogger)
            if self.log_created:
                try:
                    self.test_class_ref.logger.closeLogger()
                except Exception as ex:
                    err = funcname + " caught exception: {}".format(GetStackTraceOnException(ex))
                    print(err)
                finally:
                    self.DeleteLogger()

        def DeleteLogger(self):
            if self.test_class_ref.TestData.Resources.logger is not None:
                del self.test_class_ref.TestData.Resources.logger
                self.test_class_ref.TestData.Resources.logger = None

        def LogUnHandledExceptions(self, msg):
            filename = "unhandled_errors.txt"
            path = os.path.join(self.log_dir_path, filename)
            with open(path, "w") as f:
                f.write(msg)
                f.flush()
                f.close()

    class _TestReportManager(object):
        """
        internal class that handles test report and summary generation
        :type test_class_ref: BaseTest
        """

        def __init__(self, test_class_ref):
            self.test_class_ref = test_class_ref
            self.log_manager_ref = test_class_ref._logger_manager
            self.report_format = ReportFormat.TXT
            self.__registred_resources = OrderedDict()
            self.env_report = ""
            self.test_report = ""
            self.file_handler = self._FileHandler()
            self.error_file_handler = self._FileHandler()

        def Register_Resource(self, name=None, ref=None, dictargs=None):
            """
            register a resource to that its info will be added to report
            :param title: resource name
            :param ref: reference to resource
            :param dictargs: optional dictionary that includes resources to register and their names as keys
            NOTE** any registered resource must inherit TestDataCommon interface or implement its methods
            __str__ and To_HTML_Table
            :return:
            """
            funcname = GetFunctionName(self.Register_Resource)
            if name and ref:
                if not isinstance(ref, TestDataCommon) and (
                        not hasattr(ref, "__str__") or not hasattr(ref, "To_HTML_Table")):
                    err = funcname + "any registered resource must inherit from TestDataCommon class or implement methods {}". \
                        format("'__str__' and 'To_HTML_Table'")
                    raise TypeError(err)
                self.__registred_resources[name] = ref
            elif dictargs:
                self.__registred_resources = dictargs
                pass

        def Build_Environment_Report(self):
            """
            create a summary report for  the test environment info
            :return: report in formatted string
            :rtype:str
            """
            resource_report = ""
            for k, v in list(self.__registred_resources.items()):
                if self.report_format == ReportFormat.TXT:
                    resource_report += "\n\n{}".format(v)
                else:
                    resource_report += "\n\n{}".format(v.To_HTML_Table())
            self.env_report = resource_report
            return resource_report

        def Build_Test_Report(self):
            """
            create a summary report for the test
            :return: report in formatted string
            :rtype:str
            """
            test_report = ""
            if self.report_format == ReportFormat.TXT:
                test_report = "{}".format(self.test_class_ref.TestData.TestInfo)
                test_report += "\n\n{}".format(self.test_class_ref.TestSteps.StepsStatus)
            else:
                test_report = "{}".format(self.test_class_ref.TestData.TestInfo.To_HTML_Table())
                test_report += "\n\n{}".format(self.test_class_ref.TestSteps.StepsStatus.To_HTML_Table())
            self.test_report = test_report
            return test_report

        def Write_Environment_Report(self):
            self.Build_Environment_Report()
            self.InitFileHandler(ReportType.Environment)
            self.InitErrorFileHandler(ReportType.Environment)
            self.file_handler.Write(self.env_report)
            if len(self.test_class_ref.TestData.TestInfo._Result_Short_Message):
                self.error_file_handler.Write(
                    '"{}" "{}"'.format(self.test_class_ref.TestData.TestInfo._Result_Short_Message_Type,
                                       self.test_class_ref.TestInfo._Result_Short_Message))

        def Write_Test_Report(self):
            self.Build_Test_Report()
            if self.test_class_ref.logger is not None:
                self.InitFileHandler(ReportType.Test)
                self.InitErrorFileHandler(ReportType.Test)
                self.file_handler.Write(self.test_report)
                if len(self.test_class_ref.TestData.TestInfo._Result_Short_Message):
                    self.error_file_handler.Write(
                        '"{}" "{}"'.format(self.test_class_ref.TestData.TestInfo._Result_Short_Message_Type,
                                           self.test_class_ref.TestData.TestInfo._Result_Short_Message))
            else:
                print(self.test_report)

        def InitFileHandler(self, report_type=ReportType.Test):
            self.file_handler.extension = self.report_format.value
            if report_type == ReportType.Test:
                self.file_handler.filename = self.test_class_ref.logger._filePath.split(os.sep)[-1].split(".")[0]
                self.file_handler.filename += "_Summary"
                self.file_handler.outdir = self.log_manager_ref.log_dir_path
                if platform.system() == "Windows":
                    self.file_handler.file_path = "\\\\?\\{}\\{}.{}".format(self.file_handler.outdir
                                                                            , self.file_handler.filename,
                                                                            self.file_handler.extension)
                else:  # For Linux Access
                    self.file_handler.file_path = os.path.join(self.file_handler.outdir,
                                                               self.file_handler.filename + '.' + self.file_handler.extension)
            elif report_type == ReportType.Environment:
                # TODO: define with Chaim and Ohad where to write this report
                pass

        def InitErrorFileHandler(self, report_type=ReportType.Test):
            self.error_file_handler.extension = "summary"
            if report_type == ReportType.Test:
                self.error_file_handler.filename = self.test_class_ref.logger._filePath.split(os.sep)[-1].split(".")[0]
                self.error_file_handler.outdir = self.log_manager_ref.log_GRASS_base_path.rstrip(os.sep)
                if platform.system() == "Windows":
                    self.error_file_handler.file_path = "\\\\?\\{}\\{}.{}".format(self.error_file_handler.outdir
                                                                                  , self.error_file_handler.filename,
                                                                                  self.error_file_handler.extension)
                else:  # For Linux Access
                    self.error_file_handler.file_path = os.path.join(self.error_file_handler.outdir,
                                                                     self.error_file_handler.filename + '.' + self.error_file_handler.extension)
            elif report_type == ReportType.Environment:
                # TODO: define with Chaim and Ohad where to write this report
                pass

        class _FileHandler(object):
            """
            internal file hanlder manager for report manager
            """

            def __init__(self):
                self.outdir = ""
                self.mode = "a+"
                self.filename = ""
                self.extension = ""
                self.file_path = ""
                self.stream = None

            def Write(self, msg):
                """
                try to open and write to output file
                :param msg: message to write to
                :return: True if succeed or False otherwise
                """
                funcname = GetFunctionName(self.Write)
                res = True
                dirname = os.path.dirname(self.file_path)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)  # making sure we have the dir path created before assinging new file into it
                try:
                    self.stream = open(self.file_path, self.mode)
                    self.stream.write(msg)
                except IOError as e:
                    err = funcname + "failed to open and write to summary file at {}\nGot Error: {}\n{}" \
                        .format \
                        (self.file_path, str(e), e.strerror)
                    res = False
                finally:
                    self.stream.flush()
                    self.stream.close()
                    return res

    class _TGManager(object):
        """
        internal class to manage TG actions
        :type test_class_ref: BaseTest
        """

        def __init__(self, test_class_ref):
            # from PyInfraCommon.BaseTest.BaseTestStructures.BasetTestResources import TGConnectionsTable
            # self.connection_table = None  # type: TGConnectionsTable
            from PyInfraCommon.BaseTest.BaseTestStructures.BasetTestResources import TGMappingCollection
            self.connection_table = None  # type: TGMappingCollection
            self.chassis = None  # type: TG
            self.chassisAll = {}  # type: TG
            self.chassisTgportLink = {}  #mapping of Tgport to chassis ip
            self.tg_ports = self._TgPorts_Accesseor()
            self.logger = test_class_ref.logger  # type: BaseTestLogger
            self.is_connected = False  # indicator that tell if currently we are connected to TG
            self.cleared_ownership = False
            self.test_class_ref = test_class_ref
            self.logger = test_class_ref.logger  # type: BaseTestLogger
            self.settings = self._Settings()
            self._tg_type_excel_dict = \
                {
                    "Ixia".lower(): TGEnums.TG_TYPE.Ixia,
                    "IxNetwork".lower(): TGEnums.TG_TYPE.IxNetwork if hasattr(TGEnums.TG_TYPE, 'IxNetwork') else None,
                    "IxNetwork_RestPy".lower(): TGEnums.TG_TYPE.IxNetworkRestPy if hasattr(TGEnums.TG_TYPE,
                                                                                           'IxNetworkRestPy') else None,
                    "Ixia_IxVerify".lower(): TGEnums.TG_TYPE.IxiaVirtualSSH,
                    "Ixia_Linux".lower(): TGEnums.TG_TYPE.IxiaSSH,
                    "Ostinato".lower(): TGEnums.TG_TYPE.Ostinato,
                    "Xena".lower(): TGEnums.TG_TYPE.Xena,
                    "Spirent".lower(): TGEnums.TG_TYPE.Spirent if hasattr(TGEnums.TG_TYPE, "Spirent") else None
                }

        class _Settings(object):
            """
            internal class that holds TG settings
            """

            def __init__(self):
                self.tcl_server_ip = ""  # relevant only for IXIA & IxNetwork that uses TCL oserver
                self.tcl_server_mode = ""  # relevant only for IXIA & IxNetwork that uses TCL server
                self.remote_tcl_server = ""  # relevant only for IXIA that uses TCL server
                self.tg_type = ""
                self.port_cleanup_settings = self._PortCleanupSettings()
                self.tg_client_path = None  # path to tg client.required SW for SPIRENT or IxNetwork
                self.used_cached_connection = True # indicate if to use cached connection to save connection time( for GRAS mode)

            class _PortCleanupSettings(object):
                """
                internal class that holds cleanup settings for each tg port between tests
                """

                def __init__(self):
                    self.reset_factory_default = False
                    self.poll_tg_link_after_reset = False
                    self.clear_all_streams = None  # this option is not relevant if reset_factory_default is True

        class _TgPorts_Accesseor(object):
            def __init__(self):
                self.tg_ports = OrderedDict()  # type: dict[int,TGPort]

            def __getitem__(self, item):
                # type:(object)->TGPort
                if isinstance(item, int):
                    return self.tg_ports[str(item)]
                elif isinstance(item, str):
                    return self.tg_ports[item]

            def __setitem__(self, key, value):
                if isinstance(key, int):
                    self.tg_ports[str(key)] = value
                elif isinstance(key, str):
                    self.tg_ports[key] = value

            def items(self):
                return list(self.tg_ports.items())

            def keys(self):
                return list(self.tg_ports.keys())

            def values(self):
                return list(self.tg_ports.values())

            def get(self, k):
                if isinstance(k, int):
                    k = str(k)
                return self.tg_ports.get(k)

        def Connect(self):
            """
            connects to Tg chassis and reserve ports
            :return: True if succeeded, raises exception on failure
            :rtype:bool
            """
            result = True
            funcname = GetFunctionName(self.Connect)
            err = ""
            try:
                from .BaseTestStructures.BasetTestResources import Tg_URI
                UriList = list(self.connection_table.entries.values())
                ChassisIp2UriListDict = OrderedDict()  # type: dict(str,list[Tg_URI])
                # sort all the connection table entries by ip
                for uri in UriList:
                    if ChassisIp2UriListDict.get(uri.ip):
                        ChassisIp2UriListDict[uri.ip].append(uri)
                    else:
                        ChassisIp2UriListDict[uri.ip] = [uri]
                restore_factory_default = self.settings.port_cleanup_settings.reset_factory_default
                poll = self.settings.port_cleanup_settings.poll_tg_link_after_reset
                tcl_server_ip = ""
                user = getpass.getuser()
                pc_name = platform.uname()[1]
                logon_name = "{}@{}".format(user, pc_name)
                msg = "\n{}".format(self.connection_table)
                self.logger.trace(msg)
                clean_config_required = True
                for ip, uri_list in list(ChassisIp2UriListDict.items()):  # type: str,list[Tg_URI]
                    uri_list_fortg = [str(u) for u in uri_list]
                    tcl_server_mode = self.settings.tcl_server_mode.lower()
                    tcl_server_ip = "127.0.0.1" if "local" in tcl_server_mode else self.settings.tcl_server_ip if "remote" in tcl_server_mode else ip
                    resolved_ip = tcl_server_ip if any(
                        t in uri_list[0].type.lower() for t in ["ixia", "ixnetwork"]) else ip
                    resolved_tg_type = self._tg_type_excel_dict[uri_list[0].type.lower()]
                    msg = funcname + "connecting to {} on IP {} using TCL/API Server IP {}".format(
                        resolved_tg_type.name, ip, resolved_ip)
                    self.logger.trace(msg)
                    from PyInfraCommon.Managers.TGConnectionManager.TGConnectionsManager import TGConnectionsManager
                    tg = None
                    if self.settings.used_cached_connection:
                        tg = TGConnectionsManager.GetInstance(server_host=resolved_ip,login_name=logon_name,ports=uri_list_fortg)
                    clean_config_required = True
                    if tg is None:
                        tg = utg.connect(resolved_tg_type, resolved_ip, logon_name, rsa_path=self.settings.tg_client_path)
                        tg._logger.setLevel(logging.ERROR)
                        tg.reserve_ports(uri_list_fortg, force=True, clear=restore_factory_default)
                        # register for next time
                        if self.settings.used_cached_connection:
                            TGConnectionsManager.Register_Instance(server_host=resolved_ip,login_name=logon_name,ports=uri_list_fortg,utg_instance=tg)
                        clean_config_required = False
                        self.logger.trace(funcname + " Connection Successful")
                    else:
                        self.logger.trace(funcname+"used cached connection-Connection Successful ")
                    self.tg_ports.tg_ports.update(tg.ports)
                    self.is_connected = True

                    if not self.chassis:  # only add the first TG to be used as chassis
                        self.chassis = tg
                        self.chassis.waitLinkUpOnTx = True  # wait for linkup flag on start traffic default value
                        self.chassisAll[ip] = tg
                    else:  # when using more than 1 chassis, all other chassis will be set here
                        self.chassisAll[ip] = tg
                        self.chassisAll[ip].waitLinkUpOnTx = True  # wait for linkup flag on start traffic default value
                    self.chassisTgportLink.update({port: tg for port in tg.ports.values()})
                    self.test_class_ref.TestData.Resources.TGChassis = self.chassis
                    self.test_class_ref.TGPorts = self.tg_ports

                # Map Chassis per port and also Port 2 correct Chassis Port object
                if clean_config_required and restore_factory_default:
                    self.ResetToFactoryDefaults()
                elif self.settings.port_cleanup_settings.clear_all_streams:
                    for i, port in self.tg_ports.items():
                        port.del_all_streams(apply_to_hw=True)

                for ip, uri_list in list(ChassisIp2UriListDict.items()):  # type: str,list[Tg_URI]
                    for uri in uri_list:  # type: Tg_URI
                        if hasattr(uri, 'phy_mode'):
                            try:
                                phyMode = getattr(TGEnums.PORT_PROPERTIES_MEDIA_TYPE, uri.phy_mode.upper())
                            except AttributeError:
                                raise TestCrashedException(
                                    f"{funcname}find an invalid value for phy mode = {uri.phy_mode}")
                            self.logger.trace(f'{funcname}Found Ixia Phy Mode settings. Configure ports to {phyMode}')
                            tgPort = self.chassis.ports[str(uri.id)]
                            # Autoneg should be disabled for FIBER
                            tgPort.properties.auto_neg_enable = phyMode != TGEnums.PORT_PROPERTIES_MEDIA_TYPE.FIBER
                            try:  # This distinction is made for un-dual cards which do not support media type selection
                                tgPort.properties.media_type = phyMode
                                tgPort.apply()
                            except IxTclHalError:
                                tgPort.properties.media_type = TGEnums.PORT_PROPERTIES_MEDIA_TYPE.HW_DEFAULT
                                tgPort.apply()

                if self.test_class_ref.TestData.TestInfo._TestValidationGroup not in [TestValidationGroup.CV, TestValidationGroup.EHAL]:
                    self.UpdateTGDutPortMapping()

            except Exception as e:
                err = funcname + "failed to connect to TG ports: {}".format(GetStackTraceOnException(e))
                result = False
            finally:
                if not result:
                    self.logger.error(err)
                    raise TestCrashedException(err)
                return result

        def Disconnect(self):
            funcname = GetFunctionName(self.Disconnect)
            try:
                self.chassis.disconnect()
                self.is_connected = False
            except Exception as ex:
                self.logger.error(funcname + GetStackTraceOnException(ex))

        def Cleanup(self):
            self.StopTraffic_OnAllPorts()
            #self.Clear_Ports_OwnerShip()
            #self.Disconnect()

        def Clear_Ports_OwnerShip(self):
            """
            clears all ownership on ports
            :return: True if succeeded
            :rtype:
            """

            if not self.cleared_ownership and self.is_connected:
                funcname = GetFunctionName(self.Clear_Ports_OwnerShip)
                err = ""
                for id, port in list(self.tg_ports.items()):
                    try:
                        port.clear_ownership()
                    except Exception as e:
                        if not err:
                            err += funcname
                        err += "failed to clear ownership on port {}\n".format(self.connection_table.entries[id])

                if err:
                    self.logger.error(err)
                    return False
                else:
                    self.cleared_ownership = True

        def UpdateTGDutPortMapping(self):
            if self.connection_table is not None:
                UriList = list(self.connection_table.entries.values())
                for uri in UriList:  # type: Tg_URI
                    TGDutLink = self.test_class_ref._TG2DutPortLink()
                    TGDutLink.id = uri.id
                    TGDutLink._TG_URI_Info = uri
                    if self.tg_ports and self.tg_ports.get(uri.id):
                        TGDutLink.TGPort = self.tg_ports[uri.id]
                    if self.test_class_ref.TestData.TestInfo._TestValidationGroup == TestValidationGroup.SV:
                        from PyInfra.BaseTest_SV.SV_Enums.GenTypes import SvDutInterface
                        TGDutLink.DutDevPort = SvDutInterface(uri.dutport)
                        from PyInfra.BaseTest_SV.BaseTest_SD import BaseTest_SD
                        if isinstance(self.test_class_ref, BaseTest_SD):
                            from PyInfra.BaseTest_SV.SV_Enums.SwitchDevDutPort import SwitchDevDutPort
                            TGDutLink.DutDevPort = SwitchDevDutPort(uri.dutport)
                    elif self.test_class_ref.TestData.TestInfo._TestValidationGroup == TestValidationGroup.SONIC:
                        from PyInfra.BaseTest_CPSS_SW_MI.CPSS_SW_MI_Enums.GenTypes import SonicDutInterface
                        TGDutLink.DutDevPort = SonicDutInterface.GetInstanceFromString(uri.dutport)
                    elif self.test_class_ref.TestData.TestInfo._TestValidationGroup == TestValidationGroup.MTS:
                        from PyInfra.BaseTest_MTS.MTS_Enums.GenTypes import MTSDutInterface
                        TGDutLink.DutDevPort = MTSDutInterface(uri.dutport)

                    self.test_class_ref.TGDutLinks[uri.id] = TGDutLink
                self.test_class_ref.TGDutLinks.logger = self.logger

        def StopTraffic_OnAllPorts(self):
            funcname = GetFunctionName(self.StopTraffic_OnAllPorts)
            err = ""
            if self.is_connected and not self.cleared_ownership:
                for id, port in list(self.tg_ports.items()):
                    try:
                        port.stop_traffic()
                    except Exception as e:
                        if not err:
                            err += funcname
                        if self.connection_table.entries:
                            err += "failed to clear ownership on port {}\n".format(self.connection_table.entries[id])

        def ResetToFactoryDefaults(self):
            for i, port in list(self.tg_ports.items()):
                port.reset_factory_defaults()
                #port.del_all_streams(apply_to_hw=True)
                from UnifiedTG.IxEx.IxExChassis import IxExCard_NOVUS100
                if isinstance(self.chassis.ports[str(i)].card, IxExCard_NOVUS100):
                    port.properties.use_ieee_defaults = False
                    port.properties.auto_neg_enable = False
                    port.apply_port_config()
                    port.apply_auto_neg()

    class _LinkConnManager(object):
        """
        internal class to manage Link connections
        :type test_class_ref: BaseTest
        """

        def __init__(self, test_class_ref):
            self.test_class_ref = test_class_ref  # type: BaseTest
            self.TGManager = self.test_class_ref.TGManager

        def UpdateTGDutPortMapping(self):
            self.TGManager.UpdateTGDutPortMapping()

        def UpdateLinkConnectionTable(self):
            pass

        def UpdateTGPortInfo(self):
            pass

        def Connect(self):
            self.TGManager.Connect()
            self.UpdateTGPortInfo()

    class _TG2DutPortLink(JSONSerializable):
        """
        internal class that holds TG and Dut mapping resources
        :param DutDevPort: the Dut port object of this link
        :param TGPort: the TG port object of this link
        :param _TG_URI_Info: the uri info ( i.e. all info from this connection table row)
        """

        def __init__(self):
            self.DutDevPort = None  # type: CpssDutPort
            self.TGPort = None  # type: TGPort
            self._TG_URI_Info = None  # type: Tg_URI
            self.id = 0
            self.DutDevPortL1Config = BaseTest._TG2DutPortLink._DutDevPortL1Config()

        def __eq__(self, other):
            return self.DutDevPort == other.DutDevPort and self.TGPort._port_name == other.TGPort._port_name

        def __ne__(self, other):
            return self != other

        def __hash__(self):
            # if we want to use this class as dict keys
            return hash((self.DutDevPort.__hash__(), int(self._TG_URI_Info.id)))

        def __str__(self):
            return "Dut Port {} <==> TG Port {}".format(self.DutDevPort, self._TG_URI_Info.frindley_str())

        def table_str(self):
            table = PrettyTable()
            cols = ["Dut Port", "TG Port"]
            table.title = "Dut Port and TG Link Info"
            table.add_row([self.DutDevPort, self._TG_URI_Info.frindley_str()])
            return table.get_string()

        class _DutDevPortL1Config(object):
            def __init__(self):
                self.l1_port_fec_mode = ""
                self.l1_port_mode = ""
                self.l1_port_speed = ""
                self.use_port_manager = None

    def GetSetupXLSPath(self, forced_setup_name=None, forced_setup_list_xls_path=None):
        """
        discovers the running stations relevant setup excel path based on "Setup Name" argument or Computer name
        and build a path that is cross-platform
        :return: the final path to take excel setup from
        :rtype:str
        """
        funcname = GetFunctionName(self.GetSetupXLSPath)
        if not self._forced_setup_path:

            from PyInfraCommon.BaseTest.Paths.setup_paths import default_setups_list_path, setup_list_path_column, \
                setup_list_section_name, setup_name_path_column, setup_name_section_name
            resolved_excel_file_path = default_setups_list_path
            setup_name = ""
            resolved_attribute_column = setup_list_path_column
            resolved_section_name = setup_list_section_name
            if forced_setup_list_xls_path is None:
                forced_setup_list_xls_path = self._forced_setup_list_path
            if forced_setup_list_xls_path:  # if hasattr(self._args_object,"excel_setups_db_path") and self._args_object.excel_setups_db_path is not None:
                # user asked to override default setup db path
                resolved_excel_file_path = forced_setup_list_xls_path
                if not hasattr(self, "_printed_setups_db_path"):
                    print(
                        funcname + "received input argument -p 'excel_setups_db_path'\nsetting setups path to {}".format(
                            resolved_excel_file_path))
                    setattr(self, "_printed_setups_db_path", True)
            if forced_setup_name:  # hasattr(self._args_object, "setup_name") and self._args_object.setup_name is not None:
                # find excel path by setup name
                setup_name = forced_setup_name
                resolved_attribute_column = setup_name_path_column
                resolved_section_name = setup_name_section_name
                if not hasattr(self, "_printed_setup_name"):
                    print(funcname + "received input argument -s 'setup_name', detecting setup path by name {}".format(
                        setup_name))
                    setattr(self, "_printed_setup_name", True)

            path = ResourceManager.GetSetupPath(setup_name=setup_name,
                                                setup_list_path=resolved_excel_file_path,
                                                settings_section_name=resolved_section_name,
                                                attribute_name=resolved_attribute_column)
            # convert marvel NFS path to linux mount directory
            path = ResourceManager.FixPathForOS(path)
        else:
            path = self._forced_setup_path
        print(funcname + "Resolved Setup Excel Path is: {}".format(path))
        return path

