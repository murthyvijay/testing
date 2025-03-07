# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# generated using file ./gen/model/dent/network/interfaces/interface.yaml
#
# DONOT EDIT - generated by diligent bots

import pytest
from dent_os_testbed.lib.test_lib_object import TestLibObject
from dent_os_testbed.lib.interfaces.linux.linux_interface_impl import LinuxInterfaceImpl 
class Interface(TestLibObject):
    """
        ifupdown/ifreload - network interface management commands
        By default, ifupdown2.conf sets /etc/network/interfaces as the network interface
        configuration file. This file contains information for the ifup(8), ifdown(8) and
        ifquery(8) commands
        
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
                    impl_obj = LinuxInterfaceImpl()
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
        
    async def up(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        Interface.up(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'iface':'string_list',
                        'exclude_iface':'string_list',
                        'force':'bool',
                        'class':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        ifup [-h] [-a] [-v] [-d] [--allow CLASS] [--with-depends]
               [-X EXCLUDEPATS] [-f] [-n] [-s] [--print-dependency {list,dot}] [IFACE [IFACE ...]]
        positional arguments:
        IFACE  interface list separated by spaces. IFACE list and '-a' argument are mutually exclusive.
        optional arguments:
        -a, --all
               process all interfaces marked "auto"
        --allow CLASS
               ignore non-"allow-CLASS" interfaces
        -w, --with-depends
               run with all dependent interfaces. This option is redundant when -a is specified.
               When '-a' is specified, interfaces are always executed in dependency order.
        -X EXCLUDEPATS, --exclude EXCLUDEPATS
               Exclude interfaces from the list of interfaces to operate on. Can be specified multiple
               times If the excluded interface has dependent interfaces, (e.g. a bridge or a bond with
               multiple  enslaved  interfaces)  then each dependent interface must be specified in
               order to be excluded.
        -f, --force
               force run all operations
        -n, --no-act
               print out what would happen, but don't do it
        -p, --print-dependency {list,dot}
               print iface dependency in list or dot format
        -s, --syntax-check
               Only run the interfaces file parser
        
        """
        return await Interface._run_command("up", *argv, **kwarg)
        
    async def down(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        Interface.down(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'iface':'string_list',
                        'exclude_iface':'string_list',
                        'force':'bool',
                        'class':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        ifup [-h] [-a] [-v] [-d] [--allow CLASS] [--with-depends]
               [-X EXCLUDEPATS] [-f] [-n] [-s] [--print-dependency {list,dot}] [IFACE [IFACE ...]]
        positional arguments:
        IFACE  interface list separated by spaces. IFACE list and '-a' argument are mutually exclusive.
        optional arguments:
        -a, --all
               process all interfaces marked "auto"
        --allow CLASS
               ignore non-"allow-CLASS" interfaces
        -w, --with-depends
               run with all dependent interfaces. This option is redundant when -a is specified.
               When '-a' is specified, interfaces are always executed in dependency order.
        -X EXCLUDEPATS, --exclude EXCLUDEPATS
               Exclude interfaces from the list of interfaces to operate on. Can be specified multiple
               times If the excluded interface has dependent interfaces, (e.g. a bridge or a bond with
               multiple  enslaved  interfaces)  then each dependent interface must be specified in
               order to be excluded.
        -f, --force
               force run all operations
        -n, --no-act
               print out what would happen, but don't do it
        -p, --print-dependency {list,dot}
               print iface dependency in list or dot format
        -s, --syntax-check
               Only run the interfaces file parser
        
        """
        return await Interface._run_command("down", *argv, **kwarg)
        
    async def query(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        Interface.query(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'iface':'string_list',
                        'class':'undefined',
                        'print_dependency':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        ifquery [-v] [--allow CLASS] [--with-depends] -a|IFACE...
        ifquery [-v] [-r|--running] [--allow CLASS] [--with-depends] -a|IFACE...
        ifquery [-v] [-c|--check] [--allow CLASS] [--with-depends] -a|IFACE...
        ifquery [-v] [-p|--print-dependency {list,dot}] [--allow CLASS] [--with-depends] -a|IFACE...
        ifquery [-v] -s|--syntax-help
        positional arguments:
        IFACE   interface list separated by spaces. IFACE list and '-a' argument are mutually exclusive.
        optional arguments:
        --allow CLASS
               ignore non-"allow-CLASS" interfaces
        -w, --with-depends
               run with all dependent interfaces. This option is redundant when -a is specified.
               When '-a' is specified, interfaces are always executed in dependency order.
        -r, --running
               print raw interfaces file entries
        -c, --check
               check interface file contents against running state of an interface. Returns
               exit code 0 on success and 1 on error
        -p, --print-dependency {list,dot}
               print iface dependency in list or dot format
        -s, --syntax-help
               print supported interface config syntax. Scans all addon modules and dumps
               supported syntax from them if provided by the module.
        
        """
        return await Interface._run_command("query", *argv, **kwarg)
        
    async def reload(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        Interface.reload(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'force':'bool',
                        'exclude_iface':'string_list',
                        'options':'string',
                }],
            }],
        )
        Description:
        ifreload [-h] (-a|-c) [-v] [-d] [-f] [-n] [-s]
         -f, --force
                force run all operations
         -c, --currently-up
                Reload the configuration for all interfaces which are currently up regardless
                of whether an interface has "auto <interface>" configuration within the /etc/network/interfaces file.
         -X EXCLUDEPATS, --exclude EXCLUDEPATS
                Exclude  interfaces  from  the  list of interfaces to operate on. Can be specified
                multiple times If the excluded interface has dependent interfaces, (e.g. a bridge or
                a bond with multiple enslaved interfaces) then each dependent interface must be
                specified in order to be excluded.
         -s, --syntax-check
                Only run the interfaces file parser
        
        """
        return await Interface._run_command("reload", *argv, **kwarg)
        
