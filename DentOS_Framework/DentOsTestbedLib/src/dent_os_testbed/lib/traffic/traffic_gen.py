# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# generated using file ./gen/model/dent/traffic/traffic.yaml
#
# DONOT EDIT - generated by diligent bots

import pytest
from dent_os_testbed.lib.test_lib_object import TestLibObject
from dent_os_testbed.lib.traffic.ixnetwork.ixnetwork_ixia_client_impl import IxnetworkIxiaClientImpl 
class TrafficGen(TestLibObject):
    """
        - TrafficGen
            connect - client_addr, ports
            disconnect -
            load_config - [config_file_name]
            save_config - [config_file_name]
            set_traffic - [traffic_names], ports
            start_traffic - [traffic_names]
            stop_traffic  - [traffic_names]
            get_stats - [traffic_names]
            clear_stats - [traffic_names]
            start_protocols - [protocols]
            stop_protocols - [protocols]
            set_protocol - [protocol]
            get_protocol_stats - [protocols]
            clear_protocol_stats - [protocols]
        
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
                if device_obj.os in ['ixnetwork']:
                    impl_obj = IxnetworkIxiaClientImpl()
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
                    rc, output = impl_obj.run_command(device_obj, command=api, params=device[device_name])
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
        
    async def connect(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.connect(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'client_addr':'ip_addr_t',
                        'ports':'string_list',
                }],
            }],
        )
        Description:
        - IxiaClient
          connect - client_addr, ports
          disconnect -
        
        """
        return await TrafficGen._run_command("connect", *argv, **kwarg)
        
    async def disconnect(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.disconnect(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'client_addr':'ip_addr_t',
                        'ports':'string_list',
                }],
            }],
        )
        Description:
        - IxiaClient
          connect - client_addr, ports
          disconnect -
        
        """
        return await TrafficGen._run_command("disconnect", *argv, **kwarg)
        
    async def load_config(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.load_config(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'config_file_name':'string',
                }],
            }],
        )
        Description:
        - IxiaClient
           load_config - config_file_name
           save_config - config_file_name
        
        """
        return await TrafficGen._run_command("load_config", *argv, **kwarg)
        
    async def save_config(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.save_config(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'config_file_name':'string',
                }],
            }],
        )
        Description:
        - IxiaClient
           load_config - config_file_name
           save_config - config_file_name
        
        """
        return await TrafficGen._run_command("save_config", *argv, **kwarg)
        
    async def set_traffic(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.set_traffic(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'traffic_names':'string_list',
                        'ports':'string_list',
                }],
            }],
        )
        Description:
        - IxiaClient
           set_traffic - [traffic_names], ports
           start_traffic - [traffic_names]
           stop_traffic  - [traffic_names]
           get_stats - [traffic_names]
           clear_stats - [traffic_names]
        
        """
        return await TrafficGen._run_command("set_traffic", *argv, **kwarg)
        
    async def start_traffic(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.start_traffic(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'traffic_names':'string_list',
                        'ports':'string_list',
                }],
            }],
        )
        Description:
        - IxiaClient
           set_traffic - [traffic_names], ports
           start_traffic - [traffic_names]
           stop_traffic  - [traffic_names]
           get_stats - [traffic_names]
           clear_stats - [traffic_names]
        
        """
        return await TrafficGen._run_command("start_traffic", *argv, **kwarg)
        
    async def stop_traffic(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.stop_traffic(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'traffic_names':'string_list',
                        'ports':'string_list',
                }],
            }],
        )
        Description:
        - IxiaClient
           set_traffic - [traffic_names], ports
           start_traffic - [traffic_names]
           stop_traffic  - [traffic_names]
           get_stats - [traffic_names]
           clear_stats - [traffic_names]
        
        """
        return await TrafficGen._run_command("stop_traffic", *argv, **kwarg)
        
    async def get_stats(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.get_stats(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'traffic_names':'string_list',
                        'ports':'string_list',
                }],
            }],
        )
        Description:
        - IxiaClient
           set_traffic - [traffic_names], ports
           start_traffic - [traffic_names]
           stop_traffic  - [traffic_names]
           get_stats - [traffic_names]
           clear_stats - [traffic_names]
        
        """
        return await TrafficGen._run_command("get_stats", *argv, **kwarg)
        
    async def clear_stats(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.clear_stats(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'traffic_names':'string_list',
                        'ports':'string_list',
                }],
            }],
        )
        Description:
        - IxiaClient
           set_traffic - [traffic_names], ports
           start_traffic - [traffic_names]
           stop_traffic  - [traffic_names]
           get_stats - [traffic_names]
           clear_stats - [traffic_names]
        
        """
        return await TrafficGen._run_command("clear_stats", *argv, **kwarg)
        
    async def start_protocols(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.start_protocols(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'protocol':'undefined',
                }],
            }],
        )
        Description:
        - IxiaClient
           start_protocols - [protocols]
           stop_protocols - [protocols]
           set_protocol - [protocol]
           get_protocol_stats - [protocols]
           clear_protocol_stats - [protocols]
        
        """
        return await TrafficGen._run_command("start_protocols", *argv, **kwarg)
        
    async def stop_protocols(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.stop_protocols(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'protocol':'undefined',
                }],
            }],
        )
        Description:
        - IxiaClient
           start_protocols - [protocols]
           stop_protocols - [protocols]
           set_protocol - [protocol]
           get_protocol_stats - [protocols]
           clear_protocol_stats - [protocols]
        
        """
        return await TrafficGen._run_command("stop_protocols", *argv, **kwarg)
        
    async def set_protocol(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.set_protocol(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'protocol':'undefined',
                }],
            }],
        )
        Description:
        - IxiaClient
           start_protocols - [protocols]
           stop_protocols - [protocols]
           set_protocol - [protocol]
           get_protocol_stats - [protocols]
           clear_protocol_stats - [protocols]
        
        """
        return await TrafficGen._run_command("set_protocol", *argv, **kwarg)
        
    async def get_protocol_stats(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.get_protocol_stats(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'protocol':'undefined',
                }],
            }],
        )
        Description:
        - IxiaClient
           start_protocols - [protocols]
           stop_protocols - [protocols]
           set_protocol - [protocol]
           get_protocol_stats - [protocols]
           clear_protocol_stats - [protocols]
        
        """
        return await TrafficGen._run_command("get_protocol_stats", *argv, **kwarg)
        
    async def clear_protocol_stats(*argv, **kwarg):
        """
        Platforms: ['ixnetwork']
        Usage:
        TrafficGen.clear_protocol_stats(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'protocol':'undefined',
                }],
            }],
        )
        Description:
        - IxiaClient
           start_protocols - [protocols]
           stop_protocols - [protocols]
           set_protocol - [protocol]
           get_protocol_stats - [protocols]
           clear_protocol_stats - [protocols]
        
        """
        return await TrafficGen._run_command("clear_protocol_stats", *argv, **kwarg)
        
