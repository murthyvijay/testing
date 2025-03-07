# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# generated using file ./gen/model/dent/platform/onlp/onlpdump.yaml
#
# DONOT EDIT - generated by diligent bots

import pytest
from dent_os_testbed.lib.test_lib_object import TestLibObject
from dent_os_testbed.lib.onlp.linux.linux_onlp_system_info_impl import LinuxOnlpSystemInfoImpl 
class OnlpSystemInfo(TestLibObject):
    """
        ONLP System Level information
        
    """
    async def _run_command(api, *argv, **kwarg):
        devices = kwarg['input_data']
        result = list()
        for device in devices:
            for device_name in device:
                device_result = {
                    device_name : dict()
                }
                # device lookup
                if 'device_obj' in kwarg:
                    device_obj = kwarg.get('device_obj', None)[device_name]
                else:
                    if device_name not in pytest.testbed.devices_dict:
                        device_result[device_name] =  "No matching device "+ device_name
                        result.append(device_result)
                        return result
                    device_obj = pytest.testbed.devices_dict[device_name]
                commands = ""
                if device_obj.os in ['dentos', 'cumulus']:
                    impl_obj = LinuxOnlpSystemInfoImpl()
                    for command in device[device_name]:
                        commands += impl_obj.format_command(command=api, params=command)
                        commands += '&& '
                    commands = commands[:-3]
        
                else:
                    device_result[device_name]['rc'] = -1
                    device_result[device_name]['result'] = "No matching device OS "+ device_obj.os
                    result.append(device_result)
                    return result
                device_result[device_name]['command'] = commands
                try:
                    rc, output = await device_obj.run_cmd(("sudo " if device_obj.ssh_conn_params.pssh else "") + commands)
                    device_result[device_name]['rc'] = rc
                    device_result[device_name]['result'] = output
                    if 'parse_output' in kwarg:
                        parse_output = impl_obj.parse_output(command=api, output=output, commands=commands)
                        device_result[device_name]['parsed_output'] = parse_output
                except Exception as e:
                    device_result[device_name]['rc'] = -1
                    device_result[device_name]['result'] = str(e)
                result.append(device_result)
        return result
        
    async def show(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        OnlpSystemInfo.show(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'product_name':'string',
                        'serial_number':'string',
                        'mac':'string',
                        'mac_range':'string',
                        'manufacturer':'string',
                        'manufacturer_date':'string',
                        'vendor':'string',
                        'platform_name':'string',
                        'device_version':'string',
                        'label_revision':'string',
                        'country_code':'string',
                        'diag_version':'string',
                        'service_tag':'string',
                        'onie_version':'string',
                }],
            }],
        )
        Description:
        System Information:
         Product Name: TN48M-P
         Serial Number: TN481P2TW20220013
         MAC: 18:be:92:12:ce:9a
         MAC Range: 55
         Manufacturer: DNI
         Manufacture Date: 06/02/2020 13:24:13
         Vendor: DNI
         Platform Name: 88F7040/88F6820
         Device Version: 1
         Label Revision: C1
         Country Code: TW
         Diag Version: V1.2.1
         Service Tag: 3810000054
         ONIE Version: 2019.08-V02
        
        """
        return await OnlpSystemInfo._run_command("show", *argv, **kwarg)
        
