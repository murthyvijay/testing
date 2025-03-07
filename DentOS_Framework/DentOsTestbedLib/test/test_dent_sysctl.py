# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# generated using file ./gen/model/dent/system/os/sysctl.yaml
#
# DONOT EDIT - generated by diligent bots

import asyncio
from .utils import TestDevice
from dent_os_testbed.lib.os.sysctl import Sysctl 
def test_that_sysctl_get(capfd):
    
    dv1 = TestDevice(platform="dentos")
    dv2 = TestDevice(platform="dentos")
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(Sysctl.get(input_data = [{
        # device 1
        'test_dev' : [{}],
    }], device_obj={'test_dev':dv1}))
    print(out)
    assert 'command' in out[0]['test_dev'].keys()
    assert 'result' in out[0]['test_dev'].keys()
    # check the rc
    assert out[0]['test_dev']["rc"] == 0
    
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(Sysctl.get(input_data = [{
        # device 1
        'test_dev1' : [{
        # command 1
            'variable':'wlmoznsp',
    
        },{
        # command 2
            'variable':'dfxoranx',
    
        }],
    }], device_obj={'test_dev1':dv1, 'test_dev2':dv2}))
    print(out)
    # check if the command was formed
    assert 'command' in out[0]['test_dev1'].keys()
    # check if the result was formed
    assert 'result' in out[0]['test_dev1'].keys()
    # check the rc
    assert out[0]['test_dev1']["rc"] == 0
    
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(Sysctl.get(input_data = [{
        # device 1
        'test_dev1' : [{
            'variable':'wlmoznsp',
    
         }],
         # device 2
         'test_dev2' : [{
            'variable':'dfxoranx',
    
        }],
    }], device_obj={'test_dev1':dv1, 'test_dev2':dv2}))
    print(out)
    # check if the command was formed
    assert 'command' in out[0]['test_dev1'].keys()
    assert 'command' in out[1]['test_dev2'].keys()
    # check if the result was formed
    assert 'result' in out[0]['test_dev1'].keys()
    assert 'result' in out[1]['test_dev2'].keys()
    # check the rc
    assert out[0]['test_dev1']["rc"] == 0
    assert out[1]['test_dev2']["rc"] == 0
    
    
def test_that_sysctl_set(capfd):
    
    dv1 = TestDevice(platform="dentos")
    dv2 = TestDevice(platform="dentos")
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(Sysctl.set(input_data = [{
        # device 1
        'test_dev' : [{}],
    }], device_obj={'test_dev':dv1}))
    print(out)
    assert 'command' in out[0]['test_dev'].keys()
    assert 'result' in out[0]['test_dev'].keys()
    # check the rc
    assert out[0]['test_dev']["rc"] == 0
    
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(Sysctl.set(input_data = [{
        # device 1
        'test_dev1' : [{
        # command 1
            'variable':'eysjejvo',
            'value':'xttiqmtm',
    
        },{
        # command 2
            'variable':'frknxnkx',
            'value':'hpizjqed',
    
        }],
    }], device_obj={'test_dev1':dv1, 'test_dev2':dv2}))
    print(out)
    # check if the command was formed
    assert 'command' in out[0]['test_dev1'].keys()
    # check if the result was formed
    assert 'result' in out[0]['test_dev1'].keys()
    # check the rc
    assert out[0]['test_dev1']["rc"] == 0
    
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(Sysctl.set(input_data = [{
        # device 1
        'test_dev1' : [{
            'variable':'eysjejvo',
            'value':'xttiqmtm',
    
         }],
         # device 2
         'test_dev2' : [{
            'variable':'frknxnkx',
            'value':'hpizjqed',
    
        }],
    }], device_obj={'test_dev1':dv1, 'test_dev2':dv2}))
    print(out)
    # check if the command was formed
    assert 'command' in out[0]['test_dev1'].keys()
    assert 'command' in out[1]['test_dev2'].keys()
    # check if the result was formed
    assert 'result' in out[0]['test_dev1'].keys()
    assert 'result' in out[1]['test_dev2'].keys()
    # check the rc
    assert out[0]['test_dev1']["rc"] == 0
    assert out[1]['test_dev2']["rc"] == 0
    
    
