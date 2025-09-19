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
module: domain_management
short_description: Manage Pi-hole domain allow/block lists via pihole v6 API.
description:
    - This module adds, updates, or removes domain entries (exact or regex) on a Pi-hole instance using the piholev6api Python client.
    - Supports batch processing of multiple domain entries.
    - Maps group names to their corresponding IDs.
    - Handles both exact domain matches and regex patterns.
options:
    domains:
        description:
            - List of domain entries to manage.
        required: false
        type: list
        elements: dict
        suboptions:
            domain:
                description:
                    - Domain name or regex pattern.
                required: true
                type: str
            domain_type:
                description:
                    - Whether this is an allow or deny domain.
                required: true
                type: str
                choices: ['allow', 'deny']
            kind:
                description:
                    - Whether this is an exact match or regex pattern.
                required: true
                type: str
                choices: ['exact', 'regex']
            state:
                description:
                    - Whether the domain should be present or absent.
                required: true
                type: str
                choices: ['present', 'absent']
            comment:
                description:
                    - Optional comment for the domain.
                required: false
                type: str
                default: null
            groups:
                description:
                    - Optional list of group names. The module will map these to group IDs.
                required: false
                type: list
                elements: str
                default: []
            enabled:
                description:
                    - Whether the domain entry is enabled.
                required: false
                type: bool
                default: true
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
- name: Add exact domain to blocklist
  domain_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    domains:
      - domain: "ads.example.com"
        domain_type: "deny"
        kind: "exact"
        state: "present"
        comment: "Block ads subdomain"

- name: Add regex pattern to blocklist
  domain_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    domains:
      - domain: ".*\\.tracker\\..*"
        domain_type: "deny"
        kind: "regex"
        state: "present"
        comment: "Block tracker domains"

- name: Add domain to allowlist with groups
  domain_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    domains:
      - domain: "safe.example.com"
        domain_type: "allow"
        kind: "exact"
        state: "present"
        comment: "Safe domain"
        groups: ["Family Devices"]

- name: Remove multiple domains
  domain_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    domains:
      - domain: "unwanted.com"
        domain_type: "deny"
        kind: "exact"
        state: "absent"
      - domain: ".*\\.unwanted\\..*"
        domain_type: "deny"
        kind: "regex"
        state: "absent"
'''

RETURN = r'''
changed:
    description: Whether any changes were made
    type: bool
    returned: always
domains:
    description: List of domains that were processed
    type: list
    returned: always
results:
    description: Detailed results for each domain operation
    type: list
    returned: always
'''


def get_group_name_to_id_mapping(client):
    """Get mapping of group names to IDs."""
    try:
        groups = client.group_management.get_groups()
        return {group['name']: group['id'] for group in groups.get('groups', [])}
    except Exception as e:
        return {}


def domain_exists(client, domain, domain_type, kind):
    """Check if a domain exists."""
    try:
        result = client.domain_management.get_domain(domain, domain_type, kind)
        return result.get('success', False)
    except Exception:
        return False


def add_domain(client, domain_config, group_mapping):
    """Add a domain."""
    try:
        # Map group names to IDs
        group_ids = []
        if domain_config.get('groups'):
            for group_name in domain_config['groups']:
                if group_name in group_mapping:
                    group_ids.append(group_mapping[group_name])

        result = client.domain_management.add_domain(
            domain=domain_config['domain'],
            domain_type=domain_config['domain_type'],
            kind=domain_config['kind'],
            comment=domain_config.get('comment'),
            groups=group_ids if group_ids else None,
            enabled=domain_config.get('enabled', True)
        )
        
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def update_domain(client, domain_config, group_mapping):
    """Update an existing domain."""
    try:
        # Map group names to IDs
        group_ids = []
        if domain_config.get('groups'):
            for group_name in domain_config['groups']:
                if group_name in group_mapping:
                    group_ids.append(group_mapping[group_name])

        result = client.domain_management.update_domain(
            domain=domain_config['domain'],
            domain_type=domain_config['domain_type'],
            kind=domain_config['kind'],
            comment=domain_config.get('comment'),
            groups=group_ids if group_ids else None,
            enabled=domain_config.get('enabled', True)
        )
        
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def delete_domain(client, domain_config):
    """Delete a domain."""
    try:
        result = client.domain_management.delete_domain(
            domain=domain_config['domain'],
            domain_type=domain_config['domain_type'],
            kind=domain_config['kind']
        )
        
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def main():
    module_args = dict(
        domains=dict(
            type='list',
            elements='dict',
            required=False,
            default=[],
            options=dict(
                domain=dict(type='str', required=True),
                domain_type=dict(type='str', required=True, choices=['allow', 'deny']),
                kind=dict(type='str', required=True, choices=['exact', 'regex']),
                state=dict(type='str', required=True, choices=['present', 'absent']),
                comment=dict(type='str', required=False, default=None),
                groups=dict(type='list', elements='str', required=False, default=[]),
                enabled=dict(type='bool', required=False, default=True)
            )
        ),
        password=dict(type='str', required=True, no_log=True),
        url=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        domains=[],
        results=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_PIHOLE6API:
        module.fail_json(msg='The pihole6api Python library is required. Install it with: pip install pihole6api')

    # Get parameters
    domains = module.params['domains']
    password = module.params['password']
    url = module.params['url']

    if not domains:
        module.exit_json(**result)

    try:
        # Initialize client
        client = PiHole6Client(url, password)
        
        # Get group mapping
        group_mapping = get_group_name_to_id_mapping(client)
        
        # Process each domain
        for domain_config in domains:
            domain_result = {
                'domain': domain_config['domain'],
                'domain_type': domain_config['domain_type'],
                'kind': domain_config['kind'],
                'state': domain_config['state'],
                'changed': False,
                'success': False
            }
            
            exists = domain_exists(client, domain_config['domain'], 
                                 domain_config['domain_type'], domain_config['kind'])
            
            if domain_config['state'] == 'present':
                if exists:
                    # Update existing domain
                    if not module.check_mode:
                        success, response = update_domain(client, domain_config, group_mapping)
                        domain_result['success'] = success
                        domain_result['response'] = response
                        if success:
                            domain_result['changed'] = True
                            result['changed'] = True
                else:
                    # Add new domain
                    if not module.check_mode:
                        success, response = add_domain(client, domain_config, group_mapping)
                        domain_result['success'] = success
                        domain_result['response'] = response
                        if success:
                            domain_result['changed'] = True
                            result['changed'] = True
                    else:
                        domain_result['changed'] = True
                        result['changed'] = True
                        
            elif domain_config['state'] == 'absent':
                if exists:
                    # Delete domain
                    if not module.check_mode:
                        success, response = delete_domain(client, domain_config)
                        domain_result['success'] = success
                        domain_result['response'] = response
                        if success:
                            domain_result['changed'] = True
                            result['changed'] = True
                    else:
                        domain_result['changed'] = True
                        result['changed'] = True
            
            result['domains'].append(domain_config['domain'])
            result['results'].append(domain_result)
        
        # Close client session
        try:
            client.close_session()
        except:
            pass

    except Exception as e:
        module.fail_json(msg=f'Failed to manage domains: {to_native(e)}', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()