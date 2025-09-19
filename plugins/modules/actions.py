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
module: actions
short_description: Perform Pi-hole system actions via pihole v6 API.
description:
    - This module performs various system maintenance actions on a Pi-hole instance using the piholev6api Python client.
    - Supports flushing ARP cache, flushing DNS logs, running gravity, and restarting DNS service.
options:
    action:
        description:
            - The system action to perform.
        required: true
        type: str
        choices: ['flush_arp', 'flush_logs', 'run_gravity', 'restart_dns']
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
- name: Flush ARP cache
  actions:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "flush_arp"

- name: Flush DNS query logs
  actions:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "flush_logs"

- name: Run gravity to update blocklists
  actions:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "run_gravity"

- name: Restart DNS service
  actions:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "restart_dns"
'''

RETURN = r'''
changed:
    description: Whether the action was performed
    type: bool
    returned: always
action_performed:
    description: The action that was performed
    type: str
    returned: always
success:
    description: Whether the action was successful
    type: bool
    returned: always
response:
    description: Response from the Pi-hole API
    type: dict
    returned: always
'''


def perform_action(client, action):
    """Perform the specified action."""
    try:
        if action == 'flush_arp':
            result = client.actions.flush_arp()
        elif action == 'flush_logs':
            result = client.actions.flush_logs()
        elif action == 'run_gravity':
            result = client.actions.run_gravity()
        elif action == 'restart_dns':
            result = client.actions.restart_dns()
        else:
            return False, {'error': f'Unknown action: {action}'}
        
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def main():
    module_args = dict(
        action=dict(type='str', required=True, choices=['flush_arp', 'flush_logs', 'run_gravity', 'restart_dns']),
        password=dict(type='str', required=True, no_log=True),
        url=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        action_performed='',
        success=False,
        response={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_PIHOLE6API:
        module.fail_json(msg='The pihole6api Python library is required. Install it with: pip install pihole6api')

    # Get parameters
    action = module.params['action']
    password = module.params['password']
    url = module.params['url']

    result['action_performed'] = action

    try:
        # Initialize client
        client = PiHole6Client(url, password)
        
        if not module.check_mode:
            success, response = perform_action(client, action)
            result['success'] = success
            result['response'] = response
            
            if success:
                result['changed'] = True
            else:
                module.fail_json(msg=f'Failed to perform action {action}', **result)
        else:
            # In check mode, assume success
            result['changed'] = True
            result['success'] = True
            result['response'] = {'message': f'Would perform action: {action}'}
        
        # Close client session
        try:
            client.close_session()
        except:
            pass

    except Exception as e:
        module.fail_json(msg=f'Failed to perform action {action}: {to_native(e)}', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()