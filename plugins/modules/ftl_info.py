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
module: ftl_info
short_description: Retrieve Pi-hole FTL information via pihole v6 API.
description:
    - This module retrieves FTL (Faster Than Light) DNS server information from a Pi-hole instance using the piholev6api Python client.
    - Provides information about the FTL process status and version.
options:
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
- name: Get FTL process information
  ftl_info:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
  register: ftl_status

- name: Display FTL information
  debug:
    var: ftl_status.data

- name: Check if FTL is running
  debug:
    msg: "FTL is {{ 'running' if ftl_status.data.get('status') == 'enabled' else 'not running' }}"
'''

RETURN = r'''
success:
    description: Whether the information retrieval was successful
    type: bool
    returned: always
data:
    description: The retrieved FTL information
    type: dict
    returned: when successful
error:
    description: Error message if retrieval failed
    type: str
    returned: when failed
'''


def get_ftl_info(client):
    """Get FTL information."""
    try:
        result = client.ftl_info.get_ftl_info()
        return True, result
    except Exception as e:
        return False, {'error': to_native(e)}


def main():
    module_args = dict(
        password=dict(type='str', required=True, no_log=True),
        url=dict(type='str', required=True)
    )

    result = dict(
        success=False,
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
    password = module.params['password']
    url = module.params['url']

    try:
        # Initialize client
        client = PiHole6Client(url, password)
        
        # Get FTL information
        success, data = get_ftl_info(client)
        
        result['success'] = success
        if success:
            result['data'] = data
        else:
            result['error'] = data.get('error', 'Unknown error')
            module.fail_json(msg='Failed to retrieve FTL information', **result)
        
        # Close client session
        try:
            client.close_session()
        except:
            pass

    except Exception as e:
        result['error'] = to_native(e)
        module.fail_json(msg=f'Failed to retrieve FTL information: {to_native(e)}', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()