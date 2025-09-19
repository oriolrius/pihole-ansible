#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
import os
import tempfile

try:
    from pihole6api import PiHole6Client
    HAS_PIHOLE6API = True
except ImportError:
    HAS_PIHOLE6API = False

DOCUMENTATION = r'''
---
module: config_management
short_description: Manage Pi-hole configuration via pihole v6 API.
description:
    - This module manages Pi-hole configuration settings using the piholev6api Python client.
    - Supports getting, updating configuration, and teleporter functionality (export/import).
    - Can manage individual configuration items or full configuration updates.
options:
    action:
        description:
            - The configuration action to perform.
        required: true
        type: str
        choices: ['get', 'update', 'export', 'import', 'add_item', 'delete_item']
    config_section:
        description:
            - Specific configuration section to get (only used with 'get' action).
        required: false
        type: str
    config_changes:
        description:
            - Dictionary of configuration changes to apply (used with 'update' action).
        required: false
        type: dict
    element:
        description:
            - Configuration element name (used with 'add_item' and 'delete_item' actions).
        required: false
        type: str
    value:
        description:
            - Value to add or remove (used with 'add_item' and 'delete_item' actions).
        required: false
        type: str
    export_path:
        description:
            - Local path to save exported configuration (used with 'export' action).
        required: false
        type: str
    import_path:
        description:
            - Path to configuration file to import (used with 'import' action).
        required: false
        type: str
    import_options:
        description:
            - Import configuration options (used with 'import' action).
        required: false
        type: dict
    detailed:
        description:
            - Get detailed configuration information.
        required: false
        type: bool
        default: false
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
- name: Get current configuration
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "get"
  register: current_config

- name: Get detailed configuration
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "get"
    detailed: true

- name: Get specific configuration section
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "get"
    config_section: "dns"

- name: Update configuration
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "update"
    config_changes:
      dns_fqdn_required: true
      dns_bogus_priv: false

- name: Add configuration item
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "add_item"
    element: "dns_servers"
    value: "8.8.8.8"

- name: Remove configuration item
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "delete_item"
    element: "dns_servers"
    value: "8.8.8.8"

- name: Export configuration
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "export"
    export_path: "/tmp/pihole-backup.tar.gz"

- name: Import configuration
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "import"
    import_path: "/tmp/pihole-backup.tar.gz"
'''

RETURN = r'''
changed:
    description: Whether any changes were made
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
config:
    description: Configuration data (returned with 'get' action)
    type: dict
    returned: when action is 'get'
response:
    description: Response from the Pi-hole API
    type: dict
    returned: always
export_path:
    description: Path where configuration was exported
    type: str
    returned: when action is 'export'
'''


def get_config(client, config_section=None, detailed=False):
    """Get configuration."""
    try:
        if config_section:
            result = client.config.get_config_section(config_section, detailed)
        else:
            result = client.config.get_config(detailed)
        return True, result
    except Exception as e:
        return False, {'error': to_native(e)}


def update_config(client, config_changes):
    """Update configuration."""
    try:
        result = client.config.update_config(config_changes)
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def add_config_item(client, element, value):
    """Add configuration item."""
    try:
        result = client.config.add_config_item(element, value)
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def delete_config_item(client, element, value):
    """Delete configuration item."""
    try:
        result = client.config.delete_config_item(element, value)
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def export_config(client, export_path):
    """Export configuration."""
    try:
        binary_data = client.config.export_settings()
        with open(export_path, 'wb') as f:
            f.write(binary_data)
        return True, {'message': f'Configuration exported to {export_path}'}
    except Exception as e:
        return False, {'error': to_native(e)}


def import_config(client, import_path, import_options=None):
    """Import configuration."""
    try:
        if not os.path.exists(import_path):
            return False, {'error': f'Import file not found: {import_path}'}
        
        result = client.config.import_settings(import_path, import_options)
        return result.get('success', False), result
    except Exception as e:
        return False, {'error': to_native(e)}


def main():
    module_args = dict(
        action=dict(type='str', required=True, choices=['get', 'update', 'export', 'import', 'add_item', 'delete_item']),
        config_section=dict(type='str', required=False),
        config_changes=dict(type='dict', required=False),
        element=dict(type='str', required=False),
        value=dict(type='str', required=False),
        export_path=dict(type='str', required=False),
        import_path=dict(type='str', required=False),
        import_options=dict(type='dict', required=False),
        detailed=dict(type='bool', required=False, default=False),
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
    config_section = module.params['config_section']
    config_changes = module.params['config_changes']
    element = module.params['element']
    value = module.params['value']
    export_path = module.params['export_path']
    import_path = module.params['import_path']
    import_options = module.params['import_options']
    detailed = module.params['detailed']
    password = module.params['password']
    url = module.params['url']

    result['action_performed'] = action

    # Validate required parameters for specific actions
    if action in ['add_item', 'delete_item'] and (not element or not value):
        module.fail_json(msg=f'Action {action} requires both element and value parameters')
    
    if action == 'update' and not config_changes:
        module.fail_json(msg='Action update requires config_changes parameter')
    
    if action == 'export' and not export_path:
        module.fail_json(msg='Action export requires export_path parameter')
    
    if action == 'import' and not import_path:
        module.fail_json(msg='Action import requires import_path parameter')

    try:
        # Initialize client
        client = PiHole6Client(url, password)
        
        if action == 'get':
            success, response = get_config(client, config_section, detailed)
            result['success'] = success
            result['response'] = response
            if success:
                result['config'] = response
            
        elif action == 'update':
            if not module.check_mode:
                success, response = update_config(client, config_changes)
                result['success'] = success
                result['response'] = response
                if success:
                    result['changed'] = True
            else:
                result['changed'] = True
                result['success'] = True
                result['response'] = {'message': f'Would update configuration with: {config_changes}'}
                
        elif action == 'add_item':
            if not module.check_mode:
                success, response = add_config_item(client, element, value)
                result['success'] = success
                result['response'] = response
                if success:
                    result['changed'] = True
            else:
                result['changed'] = True
                result['success'] = True
                result['response'] = {'message': f'Would add {value} to {element}'}
                
        elif action == 'delete_item':
            if not module.check_mode:
                success, response = delete_config_item(client, element, value)
                result['success'] = success
                result['response'] = response
                if success:
                    result['changed'] = True
            else:
                result['changed'] = True
                result['success'] = True
                result['response'] = {'message': f'Would remove {value} from {element}'}
                
        elif action == 'export':
            if not module.check_mode:
                success, response = export_config(client, export_path)
                result['success'] = success
                result['response'] = response
                if success:
                    result['changed'] = True
                    result['export_path'] = export_path
            else:
                result['changed'] = True
                result['success'] = True
                result['response'] = {'message': f'Would export configuration to {export_path}'}
                result['export_path'] = export_path
                
        elif action == 'import':
            if not module.check_mode:
                success, response = import_config(client, import_path, import_options)
                result['success'] = success
                result['response'] = response
                if success:
                    result['changed'] = True
            else:
                result['changed'] = True
                result['success'] = True
                result['response'] = {'message': f'Would import configuration from {import_path}'}
        
        if not result['success'] and action != 'get':
            module.fail_json(msg=f'Failed to perform action {action}', **result)
        
        # Close client session
        try:
            client.close_session()
        except:
            pass

    except Exception as e:
        module.fail_json(msg=f'Failed to perform configuration action {action}: {to_native(e)}', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()