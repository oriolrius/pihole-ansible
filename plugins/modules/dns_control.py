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
module: dns_control
short_description: Control Pi-hole DNS blocking status via pihole v6 API.
description:
    - This module enables or disables DNS blocking on a Pi-hole instance using the piholev6api Python client.
    - Supports temporary blocking changes with timer functionality.
    - Can retrieve current blocking status.
options:
    action:
        description:
            - The action to perform.
        required: true
        type: str
        choices: ['enable', 'disable', 'status']
    timer:
        description:
            - Optional timer in seconds for temporary blocking change.
            - Only used with 'enable' or 'disable' actions.
        required: false
        type: int
        default: null
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
- name: Enable DNS blocking
  dns_control:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "enable"

- name: Disable DNS blocking for 5 minutes
  dns_control:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "disable"
    timer: 300

- name: Get current blocking status
  dns_control:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "status"
  register: blocking_status

- name: Permanently disable blocking
  dns_control:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "disable"
'''

RETURN = r'''
changed:
    description: Whether any changes were made
    type: bool
    returned: always
blocking:
    description: Current blocking status
    type: bool
    returned: always
timer:
    description: Remaining time for temporary blocking change (if applicable)
    type: int
    returned: when timer is active
action_performed:
    description: The action that was performed
    type: str
    returned: always
'''


def get_blocking_status(client):
    """Get current blocking status."""
    try:
        result = client.dns_control.get_blocking_status()
        return result.get('blocking', False), result.get('timer', 0), result
    except Exception as e:
        return None, None, {'error': to_native(e)}


def set_blocking_status(client, blocking, timer=None):
    """Set blocking status."""
    try:
        result = client.dns_control.set_blocking_status(blocking, timer)
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def main():
    module_args = dict(
        action=dict(type='str', required=True, choices=['enable', 'disable', 'status']),
        timer=dict(type='int', required=False, default=None),
        password=dict(type='str', required=True, no_log=True),
        url=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        action_performed=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_PIHOLE6API:
        module.fail_json(msg='The pihole6api Python library is required. Install it with: pip install pihole6api')

    # Get parameters
    action = module.params['action']
    timer = module.params['timer']
    password = module.params['password']
    url = module.params['url']

    try:
        # Initialize client
        client = PiHole6Client(url, password)
        
        # Get current status
        current_blocking, current_timer, status_result = get_blocking_status(client)
        
        if current_blocking is None:
            module.fail_json(msg='Failed to get current blocking status', **result)
        
        result['blocking'] = current_blocking
        if current_timer > 0:
            result['timer'] = current_timer
        
        if action == 'status':
            result['action_performed'] = 'status'
            
        elif action == 'enable':
            result['action_performed'] = 'enable'
            if not current_blocking or (current_timer > 0):
                # Need to enable blocking
                if not module.check_mode:
                    success, response = set_blocking_status(client, True, timer)
                    if success:
                        result['changed'] = True
                        result['blocking'] = True
                        if timer:
                            result['timer'] = timer
                    else:
                        module.fail_json(msg='Failed to enable blocking', response=response, **result)
                else:
                    result['changed'] = True
                    result['blocking'] = True
                    if timer:
                        result['timer'] = timer
                        
        elif action == 'disable':
            result['action_performed'] = 'disable'
            if current_blocking:
                # Need to disable blocking
                if not module.check_mode:
                    success, response = set_blocking_status(client, False, timer)
                    if success:
                        result['changed'] = True
                        result['blocking'] = False
                        if timer:
                            result['timer'] = timer
                    else:
                        module.fail_json(msg='Failed to disable blocking', response=response, **result)
                else:
                    result['changed'] = True
                    result['blocking'] = False
                    if timer:
                        result['timer'] = timer
        
        # Close client session
        try:
            client.close_session()
        except:
            pass

    except Exception as e:
        module.fail_json(msg=f'Failed to control DNS blocking: {to_native(e)}', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()