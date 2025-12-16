from pyats.topology import loader
import ipaddress
import os
import yaml
import pprint


def load_testbed_with_ssh_options(testbed_path, disable_strict_host_checking=True):
    # Load testbed YAML as dictionary first to modify it
    try:
        with open('testbed.yaml', 'r', encoding='utf-8') as f:
            testbed_dict = yaml.safe_load(f) 
        if disable_strict_host_checking is True:
        # Add ssh_options to every device's cli connection
            for device_name, device_config in testbed_dict.get('devices', {}).items():
                if 'cli' not in device_config['connections']:
                    device_config['connections']['cli'] = {}
                # Set ssh_options at the connection level (same level as protocol, ip, etc)
                    disable_str = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
                    device_config['connections']['cli']['ssh_options'] = disable_str
            return testbed_dict
        elif disable_strict_host_checking is False:
            return testbed_dict
    except:
        print("Could not find testbed file.")

    # Load the modified testbed
testbed = loader.load(testbed_dict)

for device in testbed.devices:
    device = testbed.devices[device]
    print(f"Connecting to {device.name}...")
    device.connect(init=True, via='cli', log_stdout=True)
    print("Snapshotting interface state...")
    parsed_interfaces = device.parse('show interfaces')
    

    for interface in parsed_interfaces:
        if 'ipv4' in parsed_interfaces[interface]:
            ipv4_interface_dict = parsed_interfaces[interface]['ipv4']
            ipv4_interface = ipaddress.ip_interface(next(iter(ipv4_interface_dict)))
            interface_network = ipv4_interface.network
            
            if int(interface_network.prefixlen) == 30:
                for dst_host in interface_network.hosts():
                    print(f"Pining {dst_host}")
                    ping_result = device.parse(f'ping {dst_host}')
                    success_rate = ping_result['ping']['statistics']['success_rate_percent']
                        
                        
if __name__ == "__main__":
    load_testbed_with_ssh_options('testbed.yaml', disable_strict_host_checking=True)
