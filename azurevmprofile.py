"""
Profile Fetcher for Azure VM
GitHub Repository: https://github.com/samatild/azvmprofilefetcher
"""

import requests
import json

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def replace_empty_strings(obj):
    if isinstance(obj, dict):
        return {k: replace_empty_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_empty_strings(e) for e in obj]
    elif obj == '':
        return 'N/A'
    else:
        return obj

def fetch_vm_metadata():
    url = "http://169.254.169.254/metadata/instance?api-version=2020-09-01"
    headers = {'Metadata': 'true'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        metadata = json.loads(response.text)
        return replace_empty_strings(metadata)
    else:
        raise Exception(f"Failed to fetch metadata, status code: {response.status_code}")

def print_section_header(title):
    print(f"{HEADER}{BOLD}{'=' * 40}{ENDC}")
    print(f"{HEADER}{BOLD}{title}{ENDC}")
    print(f"{HEADER}{BOLD}{'=' * 40}{ENDC}")

def print_field(name, value):
    print(f"{OKBLUE}{name}: {ENDC}{OKGREEN}{value}{ENDC}")

def display_summary(metadata):
    compute_data = metadata.get('compute', {})
    network_data = metadata.get('network', {})
    
    print_section_header("VM Details")
    for field in ['vmId', 'subscriptionId', 'resourceGroupName', 'name', 'vmSize', 'location']:
        print_field(field, compute_data.get(field, 'N/A'))
    
    print_section_header("OS Profile")
    os_profile = compute_data.get('osProfile', {})
    for field in os_profile.keys():
        print_field(field, os_profile.get(field, 'N/A'))
    
    print_section_header("Image Reference")
    image_ref = compute_data.get('storageProfile', {}).get('imageReference', {})
    for field in [k for k in image_ref.keys() if k != 'id']:
        print_field(field, image_ref.get(field, 'N/A'))
    
    print_section_header("VM Compute")
    for field in ['vmScaleSetName', 'zone', 'platformFaultDomain', 'platformUpdateDomain']:
        print_field(field, compute_data.get(field, 'N/A'))
    
    print_section_header("VM Storage")
    storage_profile = compute_data.get('storageProfile', {})
    os_disk = storage_profile.get('osDisk', {})
    data_disks = storage_profile.get('dataDisks', [])
    print_field("OS Disk", f"{os_disk.get('name', 'N/A')} ({os_disk.get('diskSizeGB', 'N/A')} GB, Caching: {os_disk.get('caching', 'N/A')}, Write Accelerator: {os_disk.get('writeAcceleratorEnabled', 'N/A')})")
    for i, disk in enumerate(data_disks):
        print_field(f"Data Disk {i+1}", f"{disk.get('name', 'N/A')} ({disk.get('diskSizeGB', 'N/A')} GB, Caching: {disk.get('caching', 'N/A')}, Write Accelerator: {disk.get('writeAcceleratorEnabled', 'N/A')})")
    
    print_section_header("VM Network")
    interfaces = network_data.get('interface', [])
    for i, interface in enumerate(interfaces):
        ipv4 = interface.get('ipv4', {})
        print_field(f"Interface {i+1}", "")
        for ip in ipv4.get('ipAddress', []):
            print_field("  IPv4", f"{ip.get('privateIpAddress', 'N/A')} (Public: {ip.get('publicIpAddress', 'N/A')})")
        for subnet in ipv4.get('subnet', []):
            print_field("  Subnet", f"{subnet.get('address', 'N/A')}/{subnet.get('prefix', 'N/A')}")

if __name__ == "__main__":
    metadata = fetch_vm_metadata()
    display_summary(metadata)
