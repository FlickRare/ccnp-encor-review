import pprint
from pyats.topology import loader

testbed = loader.load('testbed.yaml')
device = testbed.devices['R1']

print(f"Connecting to {device.name}...")
device.connect(init=True, via='cli')

print("Snapshotting interface state...")
parsed_output = device.parse('show interfaces')

pprint.pp(parsed_output)