import re

from dent_os_testbed.lib.ethtool.linux.linux_ethtool import LinuxEthtool

RE_SPACES = re.compile("\s+")


class LinuxEthtoolImpl(LinuxEthtool):
    """
    ethtool - query or control network driver and hardware settings

    """

    def format_show(self, command, *argv, **kwarg):
        """
        -a --show-pause - Queries the specified Ethernet device for pause parameter information.
        -c --show-coalesce - Queries the specified network device for coalescing information.
        -g --show-ring - Queries the specified network device for rx/tx ring parameter information.
        -i --driver Queries the specified network device for associated driver information.
        -d --register-dump Retrieves and prints a register dump for the specified network device.
           The register format for some devices is known and decoded others are printed in hex.
           When raw is enabled, then ethtool dumps the raw register data to stdout. If file is specified,
           then use contents of previous raw register dump, rather than reading from the device.
        -e --eeprom-dump Retrieves and prints an EEPROM dump for the specified network device.
           When raw is enabled, then it dumps the raw EEPROM data to stdout. The length and offset parameters
           allow dumping certain portions of the EEPROM. Default is to dump the entire EEPROM.
            raw on|off, offset N, length N
        -k --show-features --show-offload - Queries the specified network device for the state of
           protocol offload and other features.
        -P --show-permaddr - Queries the specified network device for permanent hardware address.
        -S --statistics - Queries the specified network device for NIC- and driver-specific statistics.
           --phy-statistics - Queries the specified network device for PHY specific statistics.
        -n -u --show-nfc --show-ntuple - Retrieves receive network flow classification options or rules.
           rx-flow-hash tcp4|udp4|ah4|esp4|sctp4|tcp6|udp6|ah6|esp6|sctp6
           rule N - Retrieves the RX classification rule with the given ID.
        -w --get-dump - Retrieves and prints firmware dump for the specified network device. By default,
           it prints out the dump flag, version and length of the dump data. When data is indicated,
           then ethtool fetches the dump data and directs it to a file.
        -T --show-time-stamping - Show the device's time stamping capabilities and associated PTP hardware clock.
        -x --show-rxfh-indir --show-rxfh - Retrieves the receive flow hash indirection table and/or RSS hash key.
        -l --show-channels - Queries the specified network device for the numbers of channels it has.
           A channel is an IRQ and the set of queues that can trigger that IRQ.
        -m --dump-module-eeprom --module-info - Retrieves and if possible decodes the EEPROM from plugin modules,
           e.g SFP+, QSFP. If the driver and module support it, the optical diagnostic information is also read and decoded.
        --show-priv-flags - Queries the specified network device for its private flags. The names and meanings of
           private flags (if any) are defined by each network device driver.
        --show-eee - Queries the specified network device for its support of Energy-Efficient Ethernet (according
           to the IEEE 802.3az specifications)
        --show-fec - Queries the specified network device for its support of Forward Error Correction.
        --get-phy-tunable - Gets the PHY tunable parameters.
            downshift - For operation in cabling environments that are incompatible with 1000BASE-T, PHY device provides an
             automatic link speed downshift operation. Link speed downshift after N failed 1000BASE-T auto-negotiation attempts.
             Downshift is useful where cable does not have the 4 pairs instance. Gets the PHY downshift count/status.

        """
        params = kwarg["params"]
        ############# Implement me ################
        cmd = "ethtool {} ".format(params.get("options", ""), command)
        if "devname" in params:
            cmd += "{} ".format(params["devname"])
        return cmd

    def parse_show(self, command, output, *argv, **kwarg):
        """
        root@localhost:~# ethtool swp1
        Settings for swp1:
            Supported ports: [ TP ]
            Supported link modes:   10baseT/Half 10baseT/Full
                                    100baseT/Half 100baseT/Full
                                    1000baseT/Full
            Supported pause frame use: No
            Supports auto-negotiation: Yes
            Supported FEC modes: None
            Advertised link modes:  10baseT/Half 10baseT/Full
            Advertised pause frame use: No
            Advertised auto-negotiation: Yes
            Advertised FEC modes: None
            Link partner advertised link modes:  Not reported
            Link partner advertised pause frame use: No
            Link partner advertised auto-negotiation: No
            Link partner advertised FEC modes: No
            Speed: 10Mb/s
            Duplex: Full
            Auto-negotiation: on
            Port: Twisted Pair
            PHYAD: 0
            Transceiver: internal
            MDI-X: on (auto)
            Link detected: yes
        """
        if output[0] == "b":
            output = output[2:]
        record = output
        ethtool_info = {}
        if "\\n" in record:
            records = record.split("\\n")[:-1]
        else:
            records = record.split("\n")[:-1]
        for line in records:
            line = RE_SPACES.sub(" ", line).strip().split(":")
            key = line[0].replace(" ", "_").lower()
            val = " ".join(line[1:])
            ethtool_info[key] = val
        return ethtool_info

    def format_set(self, command, *argv, **kwarg):
        """
        -G --set-ring Changes the rx/tx ring parameters of the specified network device.
           rx N Changes the number of ring entries for the Rx ring.
           rx-mini N Changes the number of ring entries for the Rx Mini ring.
           rx-jumbo N Changes the number of ring entries for the Rx Jumbo ring.
           tx N Changes the number of ring entries for the Tx ring.
        -W --set-dump - Sets the dump flag for the device.
        -X --set-rxfh-indir --rxfh - Configures the receive flow hash indirection table and/or RSS hash key.
            hkey - Sets RSS hash key of the specified network device. RSS hash key should be of device supported length.
             Hash key format must be in xx:yy:zz:aa:bb:cc format meaning both the nibbles of a byte should be mentioned even if a nibble is zero.
            hfunc - Sets RSS hash function of the specified network device. List of RSS hash functions which kernel supports
             is shown as a part of the --show-rxfh command output.
            equal N - Sets the receive flow hash indirection table to spread flows evenly between the first N receive queues.
            weight W0 W1 ... - Sets the receive flow hash indirection table to spread flows between receive queues according to
             the given weights. The sum of the weights must be non-zero and must not exceed the size of the indirection table.
            default - Sets the receive flow hash indirection table to its default value.
            context CTX | new - Specifies an RSS context to act on; either new to allocate a new RSS context, or CTX,
             a value returned by a previous ... context new.
            delete - Delete the specified RSS context. May only be used in conjunction with context and a non-zero CTX value.
        -L --set-channels - Changes the numbers of channels of the specified network device.
            rx N - Changes the number of channels with only receive queues.
            tx N - Changes the number of channels with only transmit queues.
            other N -Changes the number of channels used only for other purposes e.g. link interrupts or SR-IOV co-ordination.
            combined N - Changes the number of multi-purpose channels.
        --set-priv-flags - Sets the device's private flags as specified.
            flag on|off Sets the state of the named private flag.
        --set-eee - Sets the device EEE behaviour.
            eee on|off - Enables/disables the device support of EEE.
            tx-lpi on|off - Determines whether the device should assert its Tx LPI.
            advertise N - Sets the speeds for which the device should advertise EEE capabilities. Values are as for --change advertise
            tx-timer N - Sets the amount of time the device should stay in idle mode prior to asserting its Tx LPI
             (in microseconds). This has meaning only when Tx LPI is enabled.
        --set-phy-tunable - Sets the PHY tunable parameters.
            downshift on|off - Specifies whether downshift should be enabled
            count  N - Sets the PHY downshift re-tries count.
        --set-fec - Configures Forward Error Correction for the specified network device.
          Forward Error Correction modes selected by a user are expected to be persisted after any hotplug events.
          If a module is swapped that does not support the current FEC mode, the driver or firmware must take the
          link down administratively and report the problem in the system logs for users to correct.
            encoding auto|off|rs|baser [...] - Sets the FEC encoding for the device. Combinations of options are
             specified as e.g. encoding auto rs ; the semantics of such combinations vary between drivers.

        """
        params = kwarg["params"]
        cmd = "ethtool -s {} ".format(params.get("options", ""), command)
        if "devname" in params:
            cmd += "{} ".format(params["devname"])
        if "speed" in params:
            cmd += "speed {} ".format(params["speed"])
        if "autoneg" in params:
            cmd += "autoneg {} ".format(params["autoneg"])
        return cmd

    def parse_set(self, command, output, *argv, **kwarg):
        """
        -G --set-ring Changes the rx/tx ring parameters of the specified network device.
           rx N Changes the number of ring entries for the Rx ring.
           rx-mini N Changes the number of ring entries for the Rx Mini ring.
           rx-jumbo N Changes the number of ring entries for the Rx Jumbo ring.
           tx N Changes the number of ring entries for the Tx ring.
        -W --set-dump - Sets the dump flag for the device.
        -X --set-rxfh-indir --rxfh - Configures the receive flow hash indirection table and/or RSS hash key.
            hkey - Sets RSS hash key of the specified network device. RSS hash key should be of device supported length.
             Hash key format must be in xx:yy:zz:aa:bb:cc format meaning both the nibbles of a byte should be mentioned even if a nibble is zero.
            hfunc - Sets RSS hash function of the specified network device. List of RSS hash functions which kernel supports
             is shown as a part of the --show-rxfh command output.
            equal N - Sets the receive flow hash indirection table to spread flows evenly between the first N receive queues.
            weight W0 W1 ... - Sets the receive flow hash indirection table to spread flows between receive queues according to
             the given weights. The sum of the weights must be non-zero and must not exceed the size of the indirection table.
            default - Sets the receive flow hash indirection table to its default value.
            context CTX | new - Specifies an RSS context to act on; either new to allocate a new RSS context, or CTX,
             a value returned by a previous ... context new.
            delete - Delete the specified RSS context. May only be used in conjunction with context and a non-zero CTX value.
        -L --set-channels - Changes the numbers of channels of the specified network device.
            rx N - Changes the number of channels with only receive queues.
            tx N - Changes the number of channels with only transmit queues.
            other N -Changes the number of channels used only for other purposes e.g. link interrupts or SR-IOV co-ordination.
            combined N - Changes the number of multi-purpose channels.
        --set-priv-flags - Sets the device's private flags as specified.
            flag on|off Sets the state of the named private flag.
        --set-eee - Sets the device EEE behaviour.
            eee on|off - Enables/disables the device support of EEE.
            tx-lpi on|off - Determines whether the device should assert its Tx LPI.
            advertise N - Sets the speeds for which the device should advertise EEE capabilities. Values are as for --change advertise
            tx-timer N - Sets the amount of time the device should stay in idle mode prior to asserting its Tx LPI
             (in microseconds). This has meaning only when Tx LPI is enabled.
        --set-phy-tunable - Sets the PHY tunable parameters.
            downshift on|off - Specifies whether downshift should be enabled
            count  N - Sets the PHY downshift re-tries count.
        --set-fec - Configures Forward Error Correction for the specified network device.
          Forward Error Correction modes selected by a user are expected to be persisted after any hotplug events.
          If a module is swapped that does not support the current FEC mode, the driver or firmware must take the
          link down administratively and report the problem in the system logs for users to correct.
            encoding auto|off|rs|baser [...] - Sets the FEC encoding for the device. Combinations of options are
             specified as e.g. encoding auto rs ; the semantics of such combinations vary between drivers.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def format_change(self, command, *argv, **kwarg):
        """
        -A --pause Changes the pause parameters of the specified Ethernet device.
           autoneg on|off Specifies whether pause autonegotiation should be enabled.
           rx on|off Specifies whether RX pause should be enabled.
           tx on|off Specifies whether TX pause should be enabled.
        -C --coalesce Changes the coalescing settings of the specified network device.
        -E --change-eeprom If value is specified, changes EEPROM byte for the specified network device.
           offset and value specify which byte and it's new value. If value is not specified, stdin is
           read and written to the EEPROM. The length and offset parameters allow writing to certain
           portions of the EEPROM. Because of the persistent nature of writing to the EEPROM, a
           device-specific magic key must be specified to prevent the accidental writing to the EEPROM.
        -s --change - Allows changing some or all settings of the specified network device.
           All following options only apply if -s was specified.
            speed N - Set speed in Mb/s. ethtool with just the device name as an argument will show you the supported device speeds.
            duplex half|full - Sets full or half duplex mode.
            port tp|aui|bnc|mii - Selects device port.
            mdix auto|on|off - Selects MDI-X mode for port. May be used to override the automatic
             detection feature of most adapters. An argument of auto means automatic detection of MDI
             status, on forces MDI-X (crossover) mode, while off means MDI (straight through) mode.
             The driver should guarantee that this command takes effect immediately, and if necessary
             may reset the link to cause the change to take effect.
            autoneg on|off - Specifies whether autonegotiation should be enabled. Autonegotiation is enabled
             by default, but in some network devices may have trouble with it, so you can disable it if really necessary.
            advertise N - Sets the speed and duplex advertised by autonegotiation. The argument is a
             hexadecimal value using one or a combination of the following values: <refer man page>
            phyad N - PHY address.
            xcvr internal|external - Selects transceiver type. Currently only internal and external can be
             specified, in the future further types might be added.
            wol p|u|m|b|a|g|s|f|d... - Sets Wake-on-LAN options. Not all devices support this. The argument
             to this option is a string of characters specifying which options to enable. <refer man page>
            sopass xx:yy:zz:aa:bb:cc - Sets the SecureOn" password. The argument to this option must be 6 bytes
             in Ethernet MAC hex format (xx:yy:zz:aa:bb:cc).
            msglvl N - msglvl type on|off ... Sets the driver message type flags by name or number. type
             names the type of message to enable or disable; N specifies the new flags numerically.
             The defined type names and numbers are: <refer man page>
           The precise meanings of these type flags differ between drivers.
        -K --features --offload - Changes the offload parameters and other features of the specified
           network device. The following feature names are built-in and others may be defined by the kernel.
            rx on|off - Specifies whether RX checksumming should be enabled.
            tx on|off - Specifies whether TX checksumming should be enabled.
            sg on|off - Specifies whether scatter-gather should be enabled.
            tso on|off- Specifies whether TCP segmentation offload should be enabled.
            ufo on|off- Specifies whether UDP fragmentation offload should be enabled
            gso on|off- Specifies whether generic segmentation offload should be enabled
            gro on|off- Specifies whether generic receive offload should be enabled
            lro on|off- Specifies whether large receive offload should be enabled
            rxvlan on|off-Specifies whether RX VLAN acceleration should be enabled
            txvlan on|off-Specifies whether TX VLAN acceleration should be enabled
            ntuple on|off-Specifies whether Rx ntuple filters and actions should be enabled
            rxhash on|off-Specifies whether receive hashing offload should be enabled

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def parse_change(self, command, output, *argv, **kwarg):
        """
        -A --pause Changes the pause parameters of the specified Ethernet device.
           autoneg on|off Specifies whether pause autonegotiation should be enabled.
           rx on|off Specifies whether RX pause should be enabled.
           tx on|off Specifies whether TX pause should be enabled.
        -C --coalesce Changes the coalescing settings of the specified network device.
        -E --change-eeprom If value is specified, changes EEPROM byte for the specified network device.
           offset and value specify which byte and it's new value. If value is not specified, stdin is
           read and written to the EEPROM. The length and offset parameters allow writing to certain
           portions of the EEPROM. Because of the persistent nature of writing to the EEPROM, a
           device-specific magic key must be specified to prevent the accidental writing to the EEPROM.
        -s --change - Allows changing some or all settings of the specified network device.
           All following options only apply if -s was specified.
            speed N - Set speed in Mb/s. ethtool with just the device name as an argument will show you the supported device speeds.
            duplex half|full - Sets full or half duplex mode.
            port tp|aui|bnc|mii - Selects device port.
            mdix auto|on|off - Selects MDI-X mode for port. May be used to override the automatic
             detection feature of most adapters. An argument of auto means automatic detection of MDI
             status, on forces MDI-X (crossover) mode, while off means MDI (straight through) mode.
             The driver should guarantee that this command takes effect immediately, and if necessary
             may reset the link to cause the change to take effect.
            autoneg on|off - Specifies whether autonegotiation should be enabled. Autonegotiation is enabled
             by default, but in some network devices may have trouble with it, so you can disable it if really necessary.
            advertise N - Sets the speed and duplex advertised by autonegotiation. The argument is a
             hexadecimal value using one or a combination of the following values: <refer man page>
            phyad N - PHY address.
            xcvr internal|external - Selects transceiver type. Currently only internal and external can be
             specified, in the future further types might be added.
            wol p|u|m|b|a|g|s|f|d... - Sets Wake-on-LAN options. Not all devices support this. The argument
             to this option is a string of characters specifying which options to enable. <refer man page>
            sopass xx:yy:zz:aa:bb:cc - Sets the SecureOn" password. The argument to this option must be 6 bytes
             in Ethernet MAC hex format (xx:yy:zz:aa:bb:cc).
            msglvl N - msglvl type on|off ... Sets the driver message type flags by name or number. type
             names the type of message to enable or disable; N specifies the new flags numerically.
             The defined type names and numbers are: <refer man page>
           The precise meanings of these type flags differ between drivers.
        -K --features --offload - Changes the offload parameters and other features of the specified
           network device. The following feature names are built-in and others may be defined by the kernel.
            rx on|off - Specifies whether RX checksumming should be enabled.
            tx on|off - Specifies whether TX checksumming should be enabled.
            sg on|off - Specifies whether scatter-gather should be enabled.
            tso on|off- Specifies whether TCP segmentation offload should be enabled.
            ufo on|off- Specifies whether UDP fragmentation offload should be enabled
            gso on|off- Specifies whether generic segmentation offload should be enabled
            gro on|off- Specifies whether generic receive offload should be enabled
            lro on|off- Specifies whether large receive offload should be enabled
            rxvlan on|off-Specifies whether RX VLAN acceleration should be enabled
            txvlan on|off-Specifies whether TX VLAN acceleration should be enabled
            ntuple on|off-Specifies whether Rx ntuple filters and actions should be enabled
            rxhash on|off-Specifies whether receive hashing offload should be enabled

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def format_init(self, command, *argv, **kwarg):
        """
        -p --identify - Initiates adapter-specific action intended to enable an operator to
           easily identify the adapter by sight. Typically this involves blinking one or more
           LEDs on the specific network port.
            [ N] Length of time to perform phys-id, in seconds.
        -r --negotiate - Restarts auto-negotiation on the specified Ethernet device, if auto-negotiation is enabled.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def parse_init(self, command, output, *argv, **kwarg):
        """
        -p --identify - Initiates adapter-specific action intended to enable an operator to
           easily identify the adapter by sight. Typically this involves blinking one or more
           LEDs on the specific network port.
            [ N] Length of time to perform phys-id, in seconds.
        -r --negotiate - Restarts auto-negotiation on the specified Ethernet device, if auto-negotiation is enabled.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def format_test(self, command, *argv, **kwarg):
        """
        -t --test Executes adapter selftest on the specified network device. Possible test modes are:
            offline - Perform full set of tests, possibly interrupting normal operation during the tests,
            online - Perform limited set of tests, not interrupting normal operation,
            external_lb - Perform full set of tests, as for offline, and additionally an external-loopback test.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def parse_test(self, command, output, *argv, **kwarg):
        """
        -t --test Executes adapter selftest on the specified network device. Possible test modes are:
            offline - Perform full set of tests, possibly interrupting normal operation during the tests,
            online - Perform limited set of tests, not interrupting normal operation,
            external_lb - Perform full set of tests, as for offline, and additionally an external-loopback test.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def format_flash(self, command, *argv, **kwarg):
        """
        -f --flash - Write a firmware image to flash or other non-volatile memory on the device.
            file - Specifies the filename of the firmware image. The firmware must first be installed in one of the
             directories where the kernel firmware loader or firmware agent will look, such as /lib/firmware.
            N - If the device stores multiple firmware images in separate regions of non-volatile memory, this
             parameter may be used to specify which region is to be written. The default is 0, requesting that all
             regions are written. All other values are driver-dependent.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def parse_flash(self, command, output, *argv, **kwarg):
        """
        -f --flash - Write a firmware image to flash or other non-volatile memory on the device.
            file - Specifies the filename of the firmware image. The firmware must first be installed in one of the
             directories where the kernel firmware loader or firmware agent will look, such as /lib/firmware.
            N - If the device stores multiple firmware images in separate regions of non-volatile memory, this
             parameter may be used to specify which region is to be written. The default is 0, requesting that all
             regions are written. All other values are driver-dependent.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def format_config(self, command, *argv, **kwarg):
        """
        -N -U --config-nfc --config-ntuple - Configures receive network flow classification options or rules.
           rx-flow-hash tcp4|udp4|ah4|esp4|sctp4|tcp6|udp6|ah6|esp6|sctp6m|v|t|s|d|f|n|r...
            Configures the hash options for the specified flow type. <refer man page>
           flow-type ether|ip4|tcp4|udp4|sctp4|ah4|esp4|ip6|tcp6|udp6|ah6|esp6|sctp6
            Inserts or updates a classification rule for the specified flow type. - refer man page
           src xx:yy:zz:aa:bb:cc [m xx:yy:zz:aa:bb:cc]- Includes the source MAC address, specified as 6
            bytes in hexadecimal separated by colons, along with an optional mask. Valid only for flow-type ether.
           dst xx:yy:zz:aa:bb:cc [m xx:yy:zz:aa:bb:cc] - Includes the destination MAC address, specified as 6 bytes
            in hexadecimal separated by colons, along with an optional mask. Valid only for flow-type ether.
           proto N\[m N] - Includes the Ethernet protocol number (ethertype) and an optional mask. Valid only for flow-type ether.
           src-ip ip-address [m ip-address] - Specify the source IP address of the incoming packet to match along
            with an optional mask. Valid for all IP based flow-types.
           dst-ip ip-address [m ip-address] - Specify the destination IP address of the incoming packet to match
            along with an optional mask. Valid for all IP based flow-types.
           tos N\[m N] - Specify the value of the Type of Service field in the incoming packet to match along
            with an optional mask. Applies to all IPv4 based flow-types.
           tclass N\[m N] - Specify the value of the Traffic Class field in the incoming packet to match along
            with an optional mask. Applies to all IPv6 based flow-types.
           l4proto N\[m N] - Includes the layer 4 protocol number and optional mask. Valid only for flow-types ip4 and ip6.
           src-port N\[m N] - Specify the value of the source port field (applicable to TCP/UDP packets) in the incoming
            packet to match along with an optional mask. Valid for flow-types ip4, tcp4, udp4, and sctp4 and their IPv6 equivalents.
           dst-port N\[m N] - Specify the value of the destination port field (applicable to TCP/UDP packets)in the
            incoming packet to match along with an optional mask. Valid for flow-types ip4, tcp4, udp4, and sctp4 and their IPv6 equivalents.
           spi N\[m N] - Specify the value of the security parameter index field (applicable to AH/ESP packets)in the
            incoming packet to match along with an optional mask. Valid for flow-types ip4, ah4, and esp4 and their IPv6 equivalents.
           l4data N\[m N] - Specify the value of the first 4 Bytes of Layer 4 in the incoming packet to match along
            with an optional mask. Valid for ip4 and ip6 flow-types.
           vlan-etype N\[m N] - Includes the VLAN tag Ethertype and an optional mask.
           vlan N\[m N] - Includes the VLAN tag and an optional mask.
           user-def N\[m N] - Includes 64-bits of user-specific data and an optional mask.
           dst-mac xx:yy:zz:aa:bb:cc [m xx:yy:zz:aa:bb:cc] - Includes the destination MAC address, specified as 6 bytes
            in hexadecimal separated by colons, along with an optional mask. Valid for all IP based flow-types.
           action N - Specifies the Rx queue to send packets to, or some other action.
               -1 - Drop the matched flow, -2 - Use the matched flow as a Wake-on-LAN filter 0 or higher Rx queue to route the flow
           context N - Specifies the RSS context to spread packets over multiple queues; either 0 for the default RSS context,
            or a value returned by ethtool -X ... context new.
           vf N - Specifies the Virtual Function the filter applies to. Not compatible with action.
           queue N - Specifies the Rx queue to send packets to. Not compatible with action.
           loc N - Specify the location/ID to insert the rule. This will overwrite any rule present in that location and will not
            go through any of the rule ordering process.
           delete N - Deletes the RX classification rule with the given ID.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def parse_config(self, command, output, *argv, **kwarg):
        """
        -N -U --config-nfc --config-ntuple - Configures receive network flow classification options or rules.
           rx-flow-hash tcp4|udp4|ah4|esp4|sctp4|tcp6|udp6|ah6|esp6|sctp6m|v|t|s|d|f|n|r...
            Configures the hash options for the specified flow type. <refer man page>
           flow-type ether|ip4|tcp4|udp4|sctp4|ah4|esp4|ip6|tcp6|udp6|ah6|esp6|sctp6
            Inserts or updates a classification rule for the specified flow type. - refer man page
           src xx:yy:zz:aa:bb:cc [m xx:yy:zz:aa:bb:cc]- Includes the source MAC address, specified as 6
            bytes in hexadecimal separated by colons, along with an optional mask. Valid only for flow-type ether.
           dst xx:yy:zz:aa:bb:cc [m xx:yy:zz:aa:bb:cc] - Includes the destination MAC address, specified as 6 bytes
            in hexadecimal separated by colons, along with an optional mask. Valid only for flow-type ether.
           proto N\[m N] - Includes the Ethernet protocol number (ethertype) and an optional mask. Valid only for flow-type ether.
           src-ip ip-address [m ip-address] - Specify the source IP address of the incoming packet to match along
            with an optional mask. Valid for all IP based flow-types.
           dst-ip ip-address [m ip-address] - Specify the destination IP address of the incoming packet to match
            along with an optional mask. Valid for all IP based flow-types.
           tos N\[m N] - Specify the value of the Type of Service field in the incoming packet to match along
            with an optional mask. Applies to all IPv4 based flow-types.
           tclass N\[m N] - Specify the value of the Traffic Class field in the incoming packet to match along
            with an optional mask. Applies to all IPv6 based flow-types.
           l4proto N\[m N] - Includes the layer 4 protocol number and optional mask. Valid only for flow-types ip4 and ip6.
           src-port N\[m N] - Specify the value of the source port field (applicable to TCP/UDP packets) in the incoming
            packet to match along with an optional mask. Valid for flow-types ip4, tcp4, udp4, and sctp4 and their IPv6 equivalents.
           dst-port N\[m N] - Specify the value of the destination port field (applicable to TCP/UDP packets)in the
            incoming packet to match along with an optional mask. Valid for flow-types ip4, tcp4, udp4, and sctp4 and their IPv6 equivalents.
           spi N\[m N] - Specify the value of the security parameter index field (applicable to AH/ESP packets)in the
            incoming packet to match along with an optional mask. Valid for flow-types ip4, ah4, and esp4 and their IPv6 equivalents.
           l4data N\[m N] - Specify the value of the first 4 Bytes of Layer 4 in the incoming packet to match along
            with an optional mask. Valid for ip4 and ip6 flow-types.
           vlan-etype N\[m N] - Includes the VLAN tag Ethertype and an optional mask.
           vlan N\[m N] - Includes the VLAN tag and an optional mask.
           user-def N\[m N] - Includes 64-bits of user-specific data and an optional mask.
           dst-mac xx:yy:zz:aa:bb:cc [m xx:yy:zz:aa:bb:cc] - Includes the destination MAC address, specified as 6 bytes
            in hexadecimal separated by colons, along with an optional mask. Valid for all IP based flow-types.
           action N - Specifies the Rx queue to send packets to, or some other action.
               -1 - Drop the matched flow, -2 - Use the matched flow as a Wake-on-LAN filter 0 or higher Rx queue to route the flow
           context N - Specifies the RSS context to spread packets over multiple queues; either 0 for the default RSS context,
            or a value returned by ethtool -X ... context new.
           vf N - Specifies the Virtual Function the filter applies to. Not compatible with action.
           queue N - Specifies the Rx queue to send packets to. Not compatible with action.
           loc N - Specify the location/ID to insert the rule. This will overwrite any rule present in that location and will not
            go through any of the rule ordering process.
           delete N - Deletes the RX classification rule with the given ID.

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def format_reset(self, command, *argv, **kwarg):
        """
        --reset - Reset hardware components specified by flags and components listed below
            flags N - Resets the components based on direct flags mask
            mgmt - Management processor
            irq - Interrupt requester
            dma - DMA engine
            filter - Filtering/flow direction
            offload - Protocol offload
            mac - Media access controller
            phy - Transceiver/PHY
            ram - RAM shared between multiple components ap Application Processor
            dedicated - All components dedicated to this interface
            all - All components used by this interface, even if shared

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd

    def parse_reset(self, command, output, *argv, **kwarg):
        """
        --reset - Reset hardware components specified by flags and components listed below
            flags N - Resets the components based on direct flags mask
            mgmt - Management processor
            irq - Interrupt requester
            dma - DMA engine
            filter - Filtering/flow direction
            offload - Protocol offload
            mac - Media access controller
            phy - Transceiver/PHY
            ram - RAM shared between multiple components ap Application Processor
            dedicated - All components dedicated to this interface
            all - All components used by this interface, even if shared

        """
        params = kwarg["params"]
        cmd = "ethtool {} ".format(command)
        ############# Implement me ################

        return cmd
