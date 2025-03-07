# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# generated using file ./gen/model/dent/protocol/frr/iproute.yaml
#
# DONOT EDIT - generated by diligent bots

import asyncio

from dent_os_testbed.lib.frr.frr_ip_route import FrrIpRoute

from .utils import TestDevice


def test_that_frr_ip_route_show(capfd):

    dv1 = TestDevice(platform="dentos")
    dv2 = TestDevice(platform="dentos")
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(
        FrrIpRoute.show(
            input_data=[
                {
                    # device 1
                    "test_dev": [{}],
                }
            ],
            device_obj={"test_dev": dv1},
        )
    )
    print(out)
    assert "command" in out[0]["test_dev"].keys()
    assert "result" in out[0]["test_dev"].keys()
    # check the rc
    assert out[0]["test_dev"]["rc"] == 0

    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(
        FrrIpRoute.show(
            input_data=[
                {
                    # device 1
                    "test_dev1": [
                        {
                            # command 1
                            "network": "xwrojysi",
                            "mask": "kdwvfhdl",
                            "gateway": "hvntyuls",
                            "distance": 1267,
                            "options": "upiunzcs",
                        },
                        {
                            # command 2
                            "network": "ahxlazvl",
                            "mask": "xzhfrcei",
                            "gateway": "iszyzlzo",
                            "distance": 1575,
                            "options": "ewzyavva",
                        },
                    ],
                }
            ],
            device_obj={"test_dev1": dv1, "test_dev2": dv2},
        )
    )
    print(out)
    # check if the command was formed
    assert "command" in out[0]["test_dev1"].keys()
    # check if the result was formed
    assert "result" in out[0]["test_dev1"].keys()
    # check the rc
    assert out[0]["test_dev1"]["rc"] == 0

    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(
        FrrIpRoute.show(
            input_data=[
                {
                    # device 1
                    "test_dev1": [
                        {
                            "network": "xwrojysi",
                            "mask": "kdwvfhdl",
                            "gateway": "hvntyuls",
                            "distance": 1267,
                            "options": "upiunzcs",
                        }
                    ],
                    # device 2
                    "test_dev2": [
                        {
                            "network": "ahxlazvl",
                            "mask": "xzhfrcei",
                            "gateway": "iszyzlzo",
                            "distance": 1575,
                            "options": "ewzyavva",
                        }
                    ],
                }
            ],
            device_obj={"test_dev1": dv1, "test_dev2": dv2},
        )
    )
    print(out)
    # check if the command was formed
    assert "command" in out[0]["test_dev1"].keys()
    assert "command" in out[1]["test_dev2"].keys()
    # check if the result was formed
    assert "result" in out[0]["test_dev1"].keys()
    assert "result" in out[1]["test_dev2"].keys()
    # check the rc
    assert out[0]["test_dev1"]["rc"] == 0
    assert out[1]["test_dev2"]["rc"] == 0


def test_that_frr_ip_route_add(capfd):

    dv1 = TestDevice(platform="dentos")
    dv2 = TestDevice(platform="dentos")
    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(
        FrrIpRoute.add(
            input_data=[
                {
                    # device 1
                    "test_dev": [{}],
                }
            ],
            device_obj={"test_dev": dv1},
        )
    )
    print(out)
    assert "command" in out[0]["test_dev"].keys()
    assert "result" in out[0]["test_dev"].keys()
    # check the rc
    assert out[0]["test_dev"]["rc"] == 0

    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(
        FrrIpRoute.add(
            input_data=[
                {
                    # device 1
                    "test_dev1": [
                        {
                            # command 1
                            "network": "woqybtxk",
                            "mask": "ifktfhaz",
                            "gateway": "qldqymjv",
                            "distance": 9110,
                            "options": "eouhjira",
                        },
                        {
                            # command 2
                            "network": "izykkfiv",
                            "mask": "ieoahmml",
                            "gateway": "elortdpd",
                            "distance": 3624,
                            "options": "kwgowfzw",
                        },
                    ],
                }
            ],
            device_obj={"test_dev1": dv1, "test_dev2": dv2},
        )
    )
    print(out)
    # check if the command was formed
    assert "command" in out[0]["test_dev1"].keys()
    # check if the result was formed
    assert "result" in out[0]["test_dev1"].keys()
    # check the rc
    assert out[0]["test_dev1"]["rc"] == 0

    loop = asyncio.get_event_loop()
    out = loop.run_until_complete(
        FrrIpRoute.add(
            input_data=[
                {
                    # device 1
                    "test_dev1": [
                        {
                            "network": "woqybtxk",
                            "mask": "ifktfhaz",
                            "gateway": "qldqymjv",
                            "distance": 9110,
                            "options": "eouhjira",
                        }
                    ],
                    # device 2
                    "test_dev2": [
                        {
                            "network": "izykkfiv",
                            "mask": "ieoahmml",
                            "gateway": "elortdpd",
                            "distance": 3624,
                            "options": "kwgowfzw",
                        }
                    ],
                }
            ],
            device_obj={"test_dev1": dv1, "test_dev2": dv2},
        )
    )
    print(out)
    # check if the command was formed
    assert "command" in out[0]["test_dev1"].keys()
    assert "command" in out[1]["test_dev2"].keys()
    # check if the result was formed
    assert "result" in out[0]["test_dev1"].keys()
    assert "result" in out[1]["test_dev2"].keys()
    # check the rc
    assert out[0]["test_dev1"]["rc"] == 0
    assert out[1]["test_dev2"]["rc"] == 0
