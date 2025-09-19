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
module: metrics
short_description: Retrieve Pi-hole metrics and statistics via pihole v6 API.
description:
    - This module retrieves various metrics and statistics from a Pi-hole instance using the piholev6api Python client.
    - Supports statistics, query history, top domains/clients, and database queries.
options:
    metric_type:
        description:
            - The type of metric to retrieve.
        required: true
        type: str
        choices: ['summary', 'query_types', 'top_clients', 'top_domains', 'upstreams', 'recent_blocked', 'history', 'history_clients', 'queries', 'query_suggestions']
    blocked:
        description:
            - Filter by blocked status (only applies to top_clients and top_domains).
        required: false
        type: bool
    count:
        description:
            - Number of results to return (applies to top_clients, top_domains, recent_blocked, queries).
        required: false
        type: int
    clients:
        description:
            - Number of clients for history_clients (0 = all clients).
        required: false
        type: int
        default: 20
    start_time:
        description:
            - Start time as Unix timestamp for database queries.
        required: false
        type: int
    end_time:
        description:
            - End time as Unix timestamp for database queries.
        required: false
        type: int
    from_ts:
        description:
            - Filter queries from this Unix timestamp.
        required: false
        type: int
    until_ts:
        description:
            - Filter queries until this Unix timestamp.
        required: false
        type: int
    upstream:
        description:
            - Filter queries by upstream destination.
        required: false
        type: str
    domain:
        description:
            - Filter queries by domain (supports wildcards).
        required: false
        type: str
    client:
        description:
            - Filter queries by client.
        required: false
        type: str
    cursor:
        description:
            - Pagination cursor for query results.
        required: false
        type: str
    length:
        description:
            - Number of queries to retrieve (default: 100).
        required: false
        type: int
        default: 100
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
- name: Get Pi-hole summary statistics
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "summary"
  register: pihole_stats

- name: Get query type distribution
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "query_types"

- name: Get top 10 blocked domains
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "top_domains"
    blocked: true
    count: 10

- name: Get top clients
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "top_clients"
    count: 20

- name: Get upstream DNS statistics
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "upstreams"

- name: Get recent blocked domains
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "recent_blocked"
    count: 50

- name: Get activity history
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "history"

- name: Get per-client history
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "history_clients"
    clients: 10

- name: Get filtered query log
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "queries"
    length: 50
    domain: "*.google.com"

- name: Get query filter suggestions
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "query_suggestions"
'''

RETURN = r'''
success:
    description: Whether the metric retrieval was successful
    type: bool
    returned: always
metric_type:
    description: The type of metric that was retrieved
    type: str
    returned: always
data:
    description: The retrieved metric data
    type: dict
    returned: when successful
error:
    description: Error message if retrieval failed
    type: str
    returned: when failed
'''


def get_metric(client, metric_type, params):
    """Get the specified metric."""
    try:
        if metric_type == 'summary':
            result = client.metrics.get_stats_summary()
        elif metric_type == 'query_types':
            result = client.metrics.get_stats_query_types()
        elif metric_type == 'top_clients':
            result = client.metrics.get_stats_top_clients(
                blocked=params.get('blocked'),
                count=params.get('count')
            )
        elif metric_type == 'top_domains':
            result = client.metrics.get_stats_top_domains(
                blocked=params.get('blocked'),
                count=params.get('count')
            )
        elif metric_type == 'upstreams':
            result = client.metrics.get_stats_upstreams()
        elif metric_type == 'recent_blocked':
            result = client.metrics.get_stats_recent_blocked(
                count=params.get('count')
            )
        elif metric_type == 'history':
            result = client.metrics.get_history()
        elif metric_type == 'history_clients':
            result = client.metrics.get_history_clients(
                clients=params.get('clients', 20)
            )
        elif metric_type == 'queries':
            result = client.metrics.get_queries(
                length=params.get('length', 100),
                from_ts=params.get('from_ts'),
                until_ts=params.get('until_ts'),
                upstream=params.get('upstream'),
                domain=params.get('domain'),
                client=params.get('client'),
                cursor=params.get('cursor')
            )
        elif metric_type == 'query_suggestions':
            result = client.metrics.get_query_suggestions()
        else:
            return False, {'error': f'Unknown metric type: {metric_type}'}
        
        return True, result
    except Exception as e:
        return False, {'error': to_native(e)}


def main():
    module_args = dict(
        metric_type=dict(type='str', required=True, choices=[
            'summary', 'query_types', 'top_clients', 'top_domains', 'upstreams', 
            'recent_blocked', 'history', 'history_clients', 'queries', 'query_suggestions'
        ]),
        blocked=dict(type='bool', required=False),
        count=dict(type='int', required=False),
        clients=dict(type='int', required=False, default=20),
        start_time=dict(type='int', required=False),
        end_time=dict(type='int', required=False),
        from_ts=dict(type='int', required=False),
        until_ts=dict(type='int', required=False),
        upstream=dict(type='str', required=False),
        domain=dict(type='str', required=False),
        client=dict(type='str', required=False),
        cursor=dict(type='str', required=False),
        length=dict(type='int', required=False, default=100),
        password=dict(type='str', required=True, no_log=True),
        url=dict(type='str', required=True)
    )

    result = dict(
        success=False,
        metric_type='',
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
    metric_type = module.params['metric_type']
    password = module.params['password']
    url = module.params['url']

    result['metric_type'] = metric_type

    # Collect relevant parameters for the metric type
    params = {}
    for key in ['blocked', 'count', 'clients', 'start_time', 'end_time', 'from_ts', 
               'until_ts', 'upstream', 'domain', 'client', 'cursor', 'length']:
        if module.params[key] is not None:
            params[key] = module.params[key]

    try:
        # Initialize client
        client = PiHole6Client(url, password)
        
        # Get the metric
        success, data = get_metric(client, metric_type, params)
        
        result['success'] = success
        if success:
            result['data'] = data
        else:
            result['error'] = data.get('error', 'Unknown error')
            module.fail_json(msg=f'Failed to retrieve metric {metric_type}', **result)
        
        # Close client session
        try:
            client.close_session()
        except:
            pass

    except Exception as e:
        result['error'] = to_native(e)
        module.fail_json(msg=f'Failed to retrieve metric {metric_type}: {to_native(e)}', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()