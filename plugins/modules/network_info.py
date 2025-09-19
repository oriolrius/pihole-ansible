#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

try:
    from pihole6api import PiHole6Client
    HAS_PIHOLE6API = True
except ImportError:
    HAS_PIHOLE6API = False

DOCUMENTATION = r'''
---
module: network_info
short_description: Retrieve Pi-hole network information via pihole v6 API.
description:
    - This module retrieves network-related information from a Pi-hole instance using the piholev6api Python client.
    - Supports getting network interface information and discovered network devices.
options:
    info_type:
        description:
            - The type of network information to retrieve.
        required: true
        type: str
        choices: ['network_info', 'network_devices']
    password:
        description:
            - The API password for the Pi-hole instance.
        required: true
        type: str
        no_log: true
    url:
        description:
            - The URL of the Pi-hole instance.
        required: true
        type: str
author:
    - Automated Pi-hole Management
'''

EXAMPLES = r'''
- name: Get network interface information
  network_info:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    info_type: "network_info"
  register: network_interfaces

- name: Get discovered network devices
  network_info:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    info_type: "network_devices"
  register: network_devices

- name: Display network information
  debug:
    var: network_interfaces.data

- name: Display discovered devices
  debug:
    var: network_devices.data
'''

RETURN = r'''
success:
    description: Whether the information retrieval was successful
    type: bool
    returned: always
info_type:
    description: The type of network information that was retrieved
    type: str
    returned: always
data:
    description: The retrieved network information
    type: dict
    returned: when successful
error:
    description: Error message if retrieval failed
    type: str
    returned: when failed
'''


def get_network_info(client, info_type):
    """Get the specified network information."""
    try:
        if info_type == 'network_info':
            result = client.network_info.get_network_info()
        elif info_type == 'network_devices':
            result = client.network_info.get_network_devices()
        else:
            return False, {'error': f'Unknown info type: {info_type}'}
        
        return True, result
    except Exception as e:
        return False, {'error': to_native(e)}


def main():
    module_args = dict(
        info_type=dict(type='str', required=True, choices=['network_info', 'network_devices']),
        password=dict(type='str', required=True, no_log=True),
        url=dict(type='str', required=True)
    )

    result = dict(
        success=False,
        info_type='',
        data={},
        error=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_PIHOLE6API:
        module.fail_json(msg='The pihole6api Python library is required. Install it with: pip install pihole6api')

    # Get parameters
    info_type = module.params['info_type']
    password = module.params['password']
    url = module.params['url']

    result['info_type'] = info_type

    try:
        # Initialize client
        client = PiHole6Client(url, password)
        
        # Get the network information
        success, data = get_network_info(client, info_type)
        
        result['success'] = success
        if success:
            result['data'] = data
        else:
            result['error'] = data.get('error', 'Unknown error')
            module.fail_json(msg=f'Failed to retrieve {info_type}', **result)
        
        # Close client session
        try:
            client.close_session()
        except:
            pass

    except Exception as e:
        result['error'] = to_native(e)
        module.fail_json(msg=f'Failed to retrieve {info_type}: {to_native(e)}', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()