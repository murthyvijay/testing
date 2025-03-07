# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# generated using file ./gen/model/dent/network/ip/address.yaml
#
# DONOT EDIT - generated by diligent bots

import pytest
from dent_os_testbed.lib.test_lib_object import TestLibObject
from dent_os_testbed.lib.ip.linux.linux_ip_address_impl import LinuxIpAddressImpl 
class IpAddress(TestLibObject):
    """
        ip [ OPTIONS ] address { COMMAND | help }
        - ip address { add | change | replace } IFADDR dev IFNAME [ LIFETIME ] [ CONFFLAG-LIST ]
        - ip address del IFADDR dev IFNAME [ mngtmpaddr ]
        - ip address { save | flush } [ dev IFNAME ] [ scope SCOPE-ID ] [ metric METRIC ] [ to PREFIX ]
          [ FLAG-LIST ] [ label PATTERN ] [ up ]
        - ip address [ show [ dev IFNAME ] [ scope SCOPE-ID ] [ to PREFIX ] [ FLAG-LIST ] [ label PATTERN
          ] [ master DEVICE ] [ type TYPE ] [ vrf NAME ] [ up ] ]
        - ip address { showdump | restore }
        
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
                    impl_obj = LinuxIpAddressImpl()
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
        
    async def add(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.add(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'prefix':'ip_addr_t',
                        'peer':'ip_addr_t',
                        'broadcast':'mac_t',
                        'anycast':'ip_addr_t',
                        'label':'string',
                        'scope':'int',
                        'dev':'string',
                        'valid_lft':'undefined',
                        'preferred_lft':'undefined',
                        'confflag_list':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        Usage: ip address {add|change|replace} IFADDR dev IFNAME [ LIFETIME ] [ CONFFLAG-LIST ]
        IFADDR := PREFIX | ADDR peer PREFIX [ broadcast ADDR ] [ anycast ADDR ] [ label IFNAME ]
        [ scope SCOPE-ID ]
        SCOPE-ID := [ host | link | global | NUMBER ]
        CONFFLAG-LIST := [ CONFFLAG-LIST ] CONFFLAG
        CONFFLAG  := [ home | nodad | mngtmpaddr | noprefixroute | autojoin ]
        LIFETIME := [ valid_lft LFT ] [ preferred_lft LFT ]
        LFT := forever | SECONDS
        
        """
        return await IpAddress._run_command("add", *argv, **kwarg)
        
    async def change(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.change(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'prefix':'ip_addr_t',
                        'peer':'ip_addr_t',
                        'broadcast':'mac_t',
                        'anycast':'ip_addr_t',
                        'label':'string',
                        'scope':'int',
                        'dev':'string',
                        'valid_lft':'undefined',
                        'preferred_lft':'undefined',
                        'confflag_list':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        Usage: ip address {add|change|replace} IFADDR dev IFNAME [ LIFETIME ] [ CONFFLAG-LIST ]
        IFADDR := PREFIX | ADDR peer PREFIX [ broadcast ADDR ] [ anycast ADDR ] [ label IFNAME ]
        [ scope SCOPE-ID ]
        SCOPE-ID := [ host | link | global | NUMBER ]
        CONFFLAG-LIST := [ CONFFLAG-LIST ] CONFFLAG
        CONFFLAG  := [ home | nodad | mngtmpaddr | noprefixroute | autojoin ]
        LIFETIME := [ valid_lft LFT ] [ preferred_lft LFT ]
        LFT := forever | SECONDS
        
        """
        return await IpAddress._run_command("change", *argv, **kwarg)
        
    async def replace(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.replace(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'prefix':'ip_addr_t',
                        'peer':'ip_addr_t',
                        'broadcast':'mac_t',
                        'anycast':'ip_addr_t',
                        'label':'string',
                        'scope':'int',
                        'dev':'string',
                        'valid_lft':'undefined',
                        'preferred_lft':'undefined',
                        'confflag_list':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        Usage: ip address {add|change|replace} IFADDR dev IFNAME [ LIFETIME ] [ CONFFLAG-LIST ]
        IFADDR := PREFIX | ADDR peer PREFIX [ broadcast ADDR ] [ anycast ADDR ] [ label IFNAME ]
        [ scope SCOPE-ID ]
        SCOPE-ID := [ host | link | global | NUMBER ]
        CONFFLAG-LIST := [ CONFFLAG-LIST ] CONFFLAG
        CONFFLAG  := [ home | nodad | mngtmpaddr | noprefixroute | autojoin ]
        LIFETIME := [ valid_lft LFT ] [ preferred_lft LFT ]
        LFT := forever | SECONDS
        
        """
        return await IpAddress._run_command("replace", *argv, **kwarg)
        
    async def delete(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.delete(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'prefix':'ip_addr_t',
                        'peer':'ip_addr_t',
                        'broadcast':'mac_t',
                        'anycast':'ip_addr_t',
                        'label':'string',
                        'scope':'int',
                        'options':'string',
                }],
            }],
        )
        Description:
        ip address del IFADDR dev IFNAME [mngtmpaddr]
        IFADDR := PREFIX | ADDR peer PREFIX
               [ broadcast ADDR ] [ anycast ADDR ]
               [ label IFNAME ] [ scope SCOPE-ID ]
        SCOPE-ID := [ host | link | global | NUMBER ]
        
        """
        return await IpAddress._run_command("delete", *argv, **kwarg)
        
    async def save(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.save(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'dev':'string',
                        'scope':'int',
                        'prefix':'ip_addr_t',
                        'flag_list':'undefined',
                        'confflag_list':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        ip address {save|flush} [ dev IFNAME ] [ scope SCOPE-ID ]
                                 [ to PREFIX ] [ FLAG-LIST ] [ label LABEL ] [up]
        SCOPE-ID := [ host | link | global | NUMBER ]
        FLAG-LIST := [ FLAG-LIST ] FLAG
        FLAG  := [ permanent | dynamic | secondary | primary |
                    [-]tentative | [-]deprecated | [-]dadfailed | temporary |
                    CONFFLAG-LIST ]
        CONFFLAG-LIST := [ CONFFLAG-LIST ] CONFFLAG
        CONFFLAG  := [ home | nodad | mngtmpaddr | noprefixroute | autojoin ]
        
        """
        return await IpAddress._run_command("save", *argv, **kwarg)
        
    async def flush(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.flush(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'dev':'string',
                        'scope':'int',
                        'prefix':'ip_addr_t',
                        'flag_list':'undefined',
                        'confflag_list':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        ip address {save|flush} [ dev IFNAME ] [ scope SCOPE-ID ]
                                 [ to PREFIX ] [ FLAG-LIST ] [ label LABEL ] [up]
        SCOPE-ID := [ host | link | global | NUMBER ]
        FLAG-LIST := [ FLAG-LIST ] FLAG
        FLAG  := [ permanent | dynamic | secondary | primary |
                    [-]tentative | [-]deprecated | [-]dadfailed | temporary |
                    CONFFLAG-LIST ]
        CONFFLAG-LIST := [ CONFFLAG-LIST ] CONFFLAG
        CONFFLAG  := [ home | nodad | mngtmpaddr | noprefixroute | autojoin ]
        
        """
        return await IpAddress._run_command("flush", *argv, **kwarg)
        
    async def show(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.show(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'dev':'string',
                        'scope':'int',
                        'master':'undefined',
                        'type':'undefined',
                        'prefix':'ip_addr_t',
                        'flag_list':'undefined',
                        'confflag_list':'undefined',
                        'label':'string',
                        'vrf':'undefined',
                        'options':'string',
                }],
            }],
        )
        Description:
        ip address [ show [ dev IFNAME ] [ scope SCOPE-ID ] [ master DEVICE ]
                              [ type TYPE ] [ to PREFIX ] [ FLAG-LIST ]
                              [ label LABEL ] [up] [ vrf NAME ] ]
        FLAG-LIST := [ FLAG-LIST ] FLAG
        FLAG  := [ permanent | dynamic | secondary | primary |
                   [-]tentative | [-]deprecated | [-]dadfailed | temporary |
                   CONFFLAG-LIST ]
        CONFFLAG-LIST := [ CONFFLAG-LIST ] CONFFLAG
        CONFFLAG  := [ home | nodad | mngtmpaddr | noprefixroute | autojoin ]
        TYPE := { vlan | veth | vcan | dummy | ifb | macvlan | macvtap |
                  bridge | bond | ipoib | ip6tnl | ipip | sit | vxlan | lowpan |
                  gre | gretap | ip6gre | ip6gretap | vti | nlmon | can |
                  bond_slave | ipvlan | geneve | bridge_slave | vrf | hsr | macsec }
                 ip [ OPTIONS ] address { COMMAND | help }
        
        """
        return await IpAddress._run_command("show", *argv, **kwarg)
        
    async def showdump(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.showdump(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'options':'string',
                }],
            }],
        )
        Description:
        Restore the config
        """
        return await IpAddress._run_command("showdump", *argv, **kwarg)
        
    async def restore(*argv, **kwarg):
        """
        Platforms: ['dentos', 'cumulus']
        Usage:
        IpAddress.restore(
            input_data = [{
                # device 1
                'dev1' : [{
                    # command 1
                        'options':'string',
                }],
            }],
        )
        Description:
        Restore the config
        """
        return await IpAddress._run_command("restore", *argv, **kwarg)
        
