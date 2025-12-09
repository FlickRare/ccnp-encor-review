from pyats.topology import loader
import ipaddress
import pprint

testbed = loader.load('testbed.yaml')
for item in testbed.devices:
    device = testbed.devices[item]
    print(f"Connecting to {device.name}...")
    device.connect(init=True, via='cli', log_stdout=False)
    print("Snapshotting interface state...")
    parsed_output = device.parse('show interfaces')

    subj_interfacess = []
    for interface in parsed_output:
        if 'ipv4' in parsed_output[interface]:
            intf_ipv4_data = parsed_output[interface]['ipv4']
            split_ipv4_add = next(iter(intf_ipv4_data.values()))
            full_ipv4 = next(iter(intf_ipv4_data))
            ip = ipaddress.ip_address(split_ipv4_add['ip'])
            prefix = int(split_ipv4_add['prefix_length'])
            if prefix == 30:
                iface = ipaddress.ip_interface(full_ipv4)
                network = iface.network
                for dst_host in network.hosts():
                    if dst_host != ip:
                        print(f"Pining {dst_host}")
                        try:
                            ping_result = device.parse(f'ping {dst_host}')
                            success_rate = ping_result['ping']['statistics']['success_rate_percent']
                            assert success_rate > 50, f"Reachability failed from {device.name}, {interface}, to {dst_host}"
                            print("Success!")
                        except AssertionError as e:
                            print(e)
                        except Exception as e:
                            print(f"General failure: {e}")
                    