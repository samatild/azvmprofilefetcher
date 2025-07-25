"""
Profile Fetcher for Azure VM
GitHub Repository: https://github.com/samatild/azvmprofilefetcher
"""

import requests
import json
import argparse

HEADER = '\033[96m'  # Cyan
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
WHITE = '\033[97m'  # Bright white

USE_COLOR = True


def color(code):
    return code if USE_COLOR else ''


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
        raise Exception(
            f"Failed to fetch metadata, status code: {response.status_code}"
        )


def get_arg_parser():
    parser = argparse.ArgumentParser(description="Azure VM Profile Fetcher")
    parser.add_argument(
        '--output',
        type=str,
        help='Append output to this file instead of printing to console'
    )
    return parser


# Global output file handle
_output_file = None


def set_output_file(filename):
    global _output_file, USE_COLOR
    if filename:
        _output_file = open(
            filename, 'a', encoding='utf-8'
        )
        USE_COLOR = False
    else:
        _output_file = None
        USE_COLOR = True


def close_output_file():
    global _output_file
    if _output_file:
        _output_file.close()
        _output_file = None


def print_out(text):
    global _output_file
    if _output_file:
        _output_file.write(text + '\n')
    else:
        print(text)


def print_section_header(title):
    line = f"{color(HEADER)}{color(BOLD)}{'=' * 40}{color(ENDC)}"
    print_out(line)
    print_out(f"{color(HEADER)}{color(BOLD)}{title}{color(ENDC)}")
    print_out(line)


def print_field(name, value):
    if value == 'N/A' or value == '' or value == []:
        color_code = color(WARNING)
    elif isinstance(value, str) and value.lower().startswith('error'):
        color_code = color(FAIL)
    else:
        color_code = color(OKGREEN)
    line = (
        f"{color(WHITE)}{name}: {color(ENDC)}"
        f"{color_code}{value}{color(ENDC)}"
    )
    print_out(line)


def display_summary(metadata):
    compute_data = metadata.get('compute', {})
    network_data = metadata.get('network', {})

    print_section_header("VM Details")
    for field in [
        'vmId', 'subscriptionId', 'resourceGroupName', 'resourceId',
        'name', 'vmSize', 'location', 'azEnvironment', 'osType',
        'physicalZone', 'placementGroupId', 'zone', 'provider',
        'version', 'priority', 'evictionPolicy',
        'isHostCompatibilityLayerVm', 'licenseType', 'tags',
        'tagsList', 'userData'
    ]:
        print_field(field, compute_data.get(field, 'N/A'))

    if 'plan' in compute_data:
        print_section_header("VM Plan")
        plan = compute_data.get('plan', {})
        for field in ['name', 'product', 'publisher']:
            print_field(field, plan.get(field, 'N/A'))

    if 'extendedLocation' in compute_data:
        print_section_header("Extended Location")
        extloc = compute_data.get('extendedLocation', {})
        for field in ['type', 'name']:
            print_field(field, extloc.get(field, 'N/A'))

    if 'hostGroup' in compute_data:
        print_section_header("Host Group")
        hostgroup = compute_data.get('hostGroup', {})
        print_field('id', hostgroup.get('id', 'N/A'))
    if 'host' in compute_data:
        print_section_header("Host")
        host = compute_data.get('host', {})
        print_field('id', host.get('id', 'N/A'))

    if 'additionalCapabilities' in compute_data:
        print_section_header("Additional Capabilities")
        addcaps = compute_data.get('additionalCapabilities', {})
        for k, v in addcaps.items():
            print_field(k, v)

    print_section_header("OS Profile")
    os_profile = compute_data.get('osProfile', {})
    for field in os_profile.keys():
        print_field(field, os_profile.get(field, 'N/A'))

    print_section_header("Image Reference")
    image_ref = compute_data.get('storageProfile', {})
    image_ref = image_ref.get('imageReference', {})
    for field in ['publisher', 'offer', 'sku', 'version', 'id']:
        print_field(field, image_ref.get(field, 'N/A'))

    print_section_header("VM Compute")
    for field in [
        'vmScaleSetName',
        'virtualMachineScaleSet',
        'zone',
        'platformFaultDomain',
        'platformSubFaultDomain',
        'platformUpdateDomain',
        'publicKeys',
        'publisher',
        'offer',
        'sku',
        'plan',
        'securityProfile'
    ]:
        value = compute_data.get(field, 'N/A')
        if field == 'publicKeys' and isinstance(value, list):
            for i, key in enumerate(value):
                print_field(
                    f"Public Key {i+1}",
                    f"{key.get('path', 'N/A')}: {key.get('keyData', 'N/A')}"
                )
        elif field == 'securityProfile' and isinstance(value, dict):
            for k, v in value.items():
                print_field(f"Security {k}", v)
        elif field == 'plan' and isinstance(value, dict):
            for k, v in value.items():
                print_field(f"Plan {k}", v)
        elif field == 'virtualMachineScaleSet' and isinstance(value, dict):
            print_field('Scale Set ID', value.get('id', 'N/A'))
        else:
            print_field(field, value)

    print_section_header("VM Storage")
    storage_profile = compute_data.get('storageProfile', {})
    os_disk = storage_profile.get('osDisk', {})
    data_disks = storage_profile.get('dataDisks', [])
    resource_disk = storage_profile.get('resourceDisk', {})
    os_disk_str = (
        f"{os_disk.get('name', 'N/A')} "
        f"(Size: {os_disk.get('diskSizeGB', 'N/A')} GB, "
        f"Caching: {os_disk.get('caching', 'N/A')}, "
        f"Write Accelerator: "
        f"{os_disk.get('writeAcceleratorEnabled', 'N/A')}, "
        f"Encryption: "
        f"{os_disk.get('encryptionSettings', {}).get('enabled', 'N/A')}"
        ")"
    )
    print_field("OS Disk", os_disk_str)
    for i, disk in enumerate(data_disks):
        data_disk_str = (
            f"{disk.get('name', 'N/A')} "
            f"(Size: {disk.get('diskSizeGB', 'N/A')} GB, "
            f"Caching: {disk.get('caching', 'N/A')}, "
            f"Write Accelerator: "
            f"{disk.get('writeAcceleratorEnabled', 'N/A')}, "
            f"Encryption: "
            f"{disk.get('encryptionSettings', {}).get('enabled', 'N/A')}, "
            f"Ultra: {disk.get('isUltraDisk', 'N/A')}, "
            f"LUN: {disk.get('lun', 'N/A')})"
        )
        print_field(f"Data Disk {i+1}", data_disk_str)
    if resource_disk:
        print_field(
            "Resource Disk Size (kB)",
            resource_disk.get('size', 'N/A')
        )

    print_section_header("VM Network")
    interfaces = network_data.get('interface', [])
    for i, interface in enumerate(interfaces):
        print_field(f"Interface {i+1} MAC", interface.get('macAddress', 'N/A'))
        ipv4 = interface.get('ipv4', {})
        for ip in ipv4.get('ipAddress', []):
            print_field("  IPv4", f"{ip.get('privateIpAddress', 'N/A')} "
                        f"(Public: {ip.get('publicIpAddress', 'N/A')})")
        for subnet in ipv4.get('subnet', []):
            print_field("  Subnet", f"{subnet.get('address', 'N/A')}/"
                        f"{subnet.get('prefix', 'N/A')}")
        ipv6 = interface.get('ipv6', {})
        for ip in ipv6.get('ipAddress', []):
            print_field("  IPv6", ip.get('privateIpAddress', 'N/A'))


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()
    set_output_file(args.output)
    try:
        metadata = fetch_vm_metadata()
        display_summary(metadata)
    finally:
        close_output_file()
