import json
from dent_os_testbed.lib.bridge.linux.linux_bridge_fdb import LinuxBridgeFdb


class LinuxBridgeFdbImpl(LinuxBridgeFdb):
    """
    The corresponding commands display fdb entries, add new entries, append entries, and delete old ones.

    """

    def format_update(self, command, *argv, **kwarg):
        """
        bridge fdb { add | append | del | replace } LLADDR dev DEV { local | static | dynamic } [ self ]
          [ master ] [ router ] [ use ] [ extern_learn ] [ sticky ] [ dst IPADDR ] [ src_vni VNI ]
          [ vni VNI ] [ port PORT ] [ via DEVICE ]

        """
        params = kwarg["params"]
        cmd = "bridge fdb {} ".format(command)
        ############# Implement me ################

        return cmd

    def format_show(self, command, *argv, **kwarg):
        """
        bridge fdb [ show ] [ dev DEV ] [ br BRDEV ] [ brport DEV ] [ vlan VID ] [ state STATE ]

        """
        params = kwarg["params"]
        cmd = "bridge {} fdb {} ".format(params.get("options", ""), command)
        ############# Implement me ################

        return cmd

    def parse_show(self, command, output, *argv, **kwarg):
        return json.loads(output)
