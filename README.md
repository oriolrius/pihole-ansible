# 🍓 pihole-ansible

This collection provides comprehensive Ansible modules and roles for managing Pi-hole v6 instances via the custom API client. This collection is built on top of the [pihole6api](https://github.com/oriolrius/pihole6api) Python library (our enhanced fork), which handles authentication and requests to Pi-hole's API.

> **🚀 Enhanced Fork**: This is an enhanced version of the original pihole-ansible collection with comprehensive support for all Pi-hole v6 API features, including advanced domain management, system monitoring, configuration backup/restore, and much more.

## Overview

This collection provides complete automation capabilities for Pi-hole management, including:

### Core Modules

#### DNS Management
- **`local_a_record`**: Manage local A records for custom DNS resolution
- **`local_aaaa_record`**: Manage local AAAA (IPv6) records  
- **`local_cname`**: Manage local CNAME records for domain aliasing
- **`domain_management`**: Manage exact and regex domain allow/block rules
- **`dns_control`**: Control Pi-hole DNS blocking status (enable/disable with timers)

#### Lists Management
- **`allow_list`**: Manage allowlist URLs (domains that are always allowed)
- **`block_list`**: Manage blocklist URLs (AdLists for blocking domains)

#### Client & Group Management
- **`clients`**: Manage individual client configurations and group assignments
- **`groups`**: Manage Pi-hole groups for organizing clients and rules

#### System Operations
- **`actions`**: Perform system maintenance (flush logs, run gravity, restart DNS, flush ARP)
- **`config_management`**: Manage Pi-hole configuration and teleporter (backup/restore)
- **`metrics`**: Retrieve Pi-hole statistics, query logs, and performance data
- **`network_info`**: Get network interface and device discovery information
- **`ftl_info`**: Retrieve FTL (Faster Than Light) DNS server information

#### DHCP Management
- **`dhcp_config`**: Configure Pi-hole DHCP server settings
- **`dhcp_remove_lease`**: Remove specific DHCP leases
- **`listening_mode`**: Configure Pi-hole listening mode

### Roles

- **`manage_local_records`**: Batch management of local DNS records across multiple Pi-hole instances ([README](./roles/manage_local_records/README.md))
- **`manage_lists`**: Batch management of allow/block lists across multiple Pi-hole instances ([README](./roles/manage_lists/README.md))
- **`group_client_manager`**: Batch management of groups and clients across multiple Pi-hole instances ([README](./roles/group_client_manager/README.md))
- **`manage_proxmox_lxc_records`**: Specialized role for managing DNS records for Proxmox LXC containers ([README](./roles/manage_proxmox_lxc_records/README.md))

## 🌟 Enhanced Features

This fork includes several enhancements over the original collection:

### 🔧 **New Modules**
- **Advanced Domain Management**: Regex patterns, group assignments, batch operations
- **DNS Control**: Temporary blocking with timers, status monitoring
- **System Actions**: Automated maintenance (gravity updates, log flushing, DNS restart)
- **Configuration Management**: Full backup/restore with teleporter support
- **Comprehensive Metrics**: Statistics, query logs, performance monitoring
- **Network Discovery**: Interface information and device discovery
- **FTL Monitoring**: DNS server status and health checks

### 🚀 **Enhanced Capabilities**
- **Batch Processing**: Handle multiple operations efficiently
- **Group-based Management**: Advanced client and domain organization
- **Real-time Monitoring**: Live statistics and query analysis
- **Automated Backups**: Configuration export/import with versioning
- **Advanced Filtering**: Query logs with time ranges and pattern matching

## Getting Started

### Prerequisites

- **Ansible:** Version 2.9 or later
- **Python:** The control node requires Python 3.7+
- **pihole6api Library:** Our enhanced fork is required for all modules to function

### Installation

#### Install from Our Fork

```bash
# Clone and install our enhanced collection
git clone https://github.com/oriolrius/pihole-ansible
cd pihole-ansible
ansible-galaxy collection build
ansible-galaxy collection install *.tar.gz
```

### Installing pihole6api Dependency

The `pihole6api` library (our enhanced fork) is **required** for this collection. Choose the installation method that matches your Ansible setup:

#### Option 1: Virtual Environment (Recommended)

Create an isolated environment for Ansible and dependencies:

```bash
python -m venv ~/.venv
source ~/.venv/bin/activate  # On Windows: ~/.venv/Scripts/activate
pip install ansible git+https://github.com/oriolrius/pihole6api.git
```

Configure Ansible to use this environment by setting in `ansible.cfg`:

```ini
[defaults]
interpreter_python = ~/.venv/bin/python
```

#### Option 2: pipx Environment

If Ansible was installed via pipx:

```bash
pipx inject ansible git+https://github.com/oriolrius/pihole6api.git --include-deps
```

Configure `ansible.cfg`:

```ini
[defaults]
interpreter_python = ~/.local/pipx/venvs/ansible/bin/python
```

#### Option 3: System-wide Installation

For system Ansible installations (not recommended for modern distributions):

```bash
pip install --break-system-packages git+https://github.com/oriolrius/pihole6api.git
# or
sudo pip install git+https://github.com/oriolrius/pihole6api.git
```

### Verification

Test your installation:

```bash
ansible --version
python -c "import pihole6api; print('pihole6api successfully installed')"
```

## Module Reference

### DNS Management Modules

#### local_a_record
Manage local A records for custom DNS resolution.

**Key Parameters:**
- `host`: Hostname for the A record
- `ip`: IP address to associate with hostname
- `state`: `present` or `absent`

**Example:**
```yaml
- name: Create local A record
  local_a_record:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    host: "myserver.local"
    ip: "192.168.1.100"
    state: present
```

#### local_cname
Manage local CNAME records for domain aliasing.

**Example:**
```yaml
- name: Create CNAME alias
  local_cname:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    source: "www.myserver.local"
    target: "myserver.local"
    state: present
```

#### domain_management
Manage exact and regex domain allow/block rules with advanced group assignment.

**Key Features:**
- Support for exact domain matches and regex patterns
- Group-based rule assignment
- Batch processing of multiple domains
- Comprehensive commenting and metadata

**Example:**
```yaml
- name: Manage domain rules
  domain_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    domains:
      - domain: "ads.tracker.com"
        domain_type: "deny"
        kind: "exact"
        state: "present"
        comment: "Block advertising tracker"
        groups: ["Adults"]
      - domain: ".*\\.doubleclick\\..*"
        domain_type: "deny"
        kind: "regex"
        state: "present"
        comment: "Block all DoubleClick domains"
```

#### dns_control
Control Pi-hole DNS blocking status with timer support.

**Example:**
```yaml
- name: Temporarily disable blocking for 5 minutes
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
```

### List Management Modules

#### allow_list / block_list
Manage allowlist and blocklist URLs (AdLists).

**Example:**
```yaml
- name: Manage block lists
  block_list:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    lists:
      - address: "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
        state: "present"
        comment: "Steven Black's unified hosts file"
        groups: ["Default"]
```

### System Operations Modules

#### actions
Perform system maintenance operations.

**Available Actions:**
- `flush_arp`: Clear network ARP cache
- `flush_logs`: Clear DNS query logs
- `run_gravity`: Update all blocklists
- `restart_dns`: Restart FTL DNS service

**Example:**
```yaml
- name: Update blocklists
  actions:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "run_gravity"

- name: Restart DNS service
  actions:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "restart_dns"
```

#### config_management
Comprehensive configuration management with teleporter support.

**Available Actions:**
- `get`: Retrieve current configuration
- `update`: Modify configuration settings
- `export`: Backup configuration to file
- `import`: Restore configuration from backup
- `add_item`/`delete_item`: Manage configuration arrays

**Example:**
```yaml
- name: Backup Pi-hole configuration
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "export"
    export_path: "/tmp/pihole-backup-{{ ansible_date_time.epoch }}.tar.gz"

- name: Update DNS settings
  config_management:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    action: "update"
    config_changes:
      dns_fqdn_required: true
      dns_bogus_priv: false
```

#### metrics
Retrieve comprehensive Pi-hole statistics and metrics.

**Available Metrics:**
- `summary`: Overall Pi-hole statistics
- `query_types`: Query type distribution
- `top_clients`/`top_domains`: Top traffic sources
- `upstreams`: Upstream DNS server stats
- `recent_blocked`: Recently blocked domains
- `history`: Query activity over time
- `queries`: Detailed query log with filtering

**Example:**
```yaml
- name: Get Pi-hole summary stats
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "summary"
  register: pihole_stats

- name: Get top 10 blocked domains
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "top_domains"
    blocked: true
    count: 10

- name: Get filtered query log
  metrics:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    metric_type: "queries"
    length: 100
    domain: "*.google.com"
    from_ts: "{{ (ansible_date_time.epoch | int) - 3600 }}"
```

### Information Modules

#### network_info
Retrieve network interface and device discovery information.

**Example:**
```yaml
- name: Get network interfaces
  network_info:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    info_type: "network_info"

- name: Discover network devices
  network_info:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
    info_type: "network_devices"
```

#### ftl_info
Get FTL (Faster Than Light) DNS server status and version information.

**Example:**
```yaml
- name: Check FTL status
  ftl_info:
    url: "http://pi.hole"
    password: "{{ pihole_password }}"
  register: ftl_status
```

## Advanced Usage Examples

### Complete Pi-hole Setup Playbook

```yaml
---
- name: Complete Pi-hole configuration
  hosts: pihole_servers
  vars:
    pihole_password: "{{ vault_pihole_password }}"
  tasks:
    # 1. Configure basic settings
    - name: Update Pi-hole configuration
      config_management:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        action: "update"
        config_changes:
          dns_fqdn_required: true
          dns_bogus_priv: true
          
    # 2. Set up groups
    - name: Create device groups
      groups:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        groups:
          - name: "Kids Devices"
            comment: "Devices for children with strict filtering"
            state: "present"
          - name: "Adult Devices"
            comment: "Devices for adults with normal filtering"
            state: "present"
            
    # 3. Add comprehensive block lists
    - name: Configure block lists
      block_list:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        lists:
          - address: "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
            state: "present"
            comment: "Steven Black's unified hosts file"
          - address: "https://someonewhocares.org/hosts/zero/hosts"
            state: "present"
            comment: "Dan Pollock's hosts file"
            
    # 4. Add local DNS records
    - name: Create local DNS records
      local_a_record:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        host: "{{ item.host }}"
        ip: "{{ item.ip }}"
        state: "present"
      loop:
        - { host: "nas.local", ip: "192.168.1.10" }
        - { host: "router.local", ip: "192.168.1.1" }
        - { host: "homeassistant.local", ip: "192.168.1.20" }
        
    # 5. Configure domain rules
    - name: Set up domain blocking rules
      domain_management:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        domains:
          - domain: ".*\\.facebook\\.com"
            domain_type: "deny"
            kind: "regex"
            state: "present"
            comment: "Block Facebook domains for kids"
            groups: ["Kids Devices"]
          - domain: "educational.example.com"
            domain_type: "allow"
            kind: "exact"
            state: "present"
            comment: "Always allow educational sites"
            
    # 6. Update block lists
    - name: Run gravity to update all lists
      actions:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        action: "run_gravity"
        
    # 7. Create backup
    - name: Backup configuration
      config_management:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        action: "export"
        export_path: "/tmp/pihole-backup-{{ inventory_hostname }}-{{ ansible_date_time.epoch }}.tar.gz"
```

### Monitoring and Maintenance Playbook

```yaml
---
- name: Pi-hole monitoring and maintenance
  hosts: pihole_servers
  vars:
    pihole_password: "{{ vault_pihole_password }}"
  tasks:
    # Get comprehensive stats
    - name: Gather Pi-hole statistics
      metrics:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        metric_type: "summary"
      register: stats
      
    - name: Display statistics
      debug:
        msg: |
          Pi-hole {{ inventory_hostname }} Statistics:
          Total Queries: {{ stats.data.total_queries }}
          Blocked Queries: {{ stats.data.blocked_queries }}
          Block Percentage: {{ ((stats.data.blocked_queries / stats.data.total_queries) * 100) | round(2) }}%
          
    # Check system health
    - name: Check FTL status
      ftl_info:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
      register: ftl_status
      
    - name: Verify FTL is running
      assert:
        that: ftl_status.data.status == "enabled"
        fail_msg: "FTL is not running properly on {{ inventory_hostname }}"
        
    # Maintenance tasks
    - name: Flush old logs weekly
      actions:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        action: "flush_logs"
      when: ansible_date_time.weekday == "0"  # Sunday
      
    - name: Update blocklists daily
      actions:
        url: "http://{{ inventory_hostname }}"
        password: "{{ pihole_password }}"
        action: "run_gravity"
      when: ansible_date_time.hour == "02"  # 2 AM
```

## Role Usage

The collection includes several roles for managing multiple Pi-hole instances:

### manage_local_records Role

```yaml
- name: Manage DNS records across Pi-hole instances
  include_role:
    name: manage_local_records
  vars:
    pihole_hosts:
      - name: "primary-pihole"
        url: "http://192.168.1.10"
        password: "{{ vault_primary_password }}"
      - name: "secondary-pihole"
        url: "http://192.168.1.11"
        password: "{{ vault_secondary_password }}"
    local_records:
      a_records:
        - { host: "nas.local", ip: "192.168.1.20" }
        - { host: "printer.local", ip: "192.168.1.30" }
      cname_records:
        - { source: "www.nas.local", target: "nas.local" }
```

## Best Practices

### Security
- Store Pi-hole passwords in Ansible Vault
- Use group-based access controls
- Regular configuration backups
- Monitor for unauthorized changes

### Performance
- Run gravity updates during low-traffic periods
- Use check mode for testing changes
- Batch operations when possible
- Monitor Pi-hole performance metrics

### Maintenance
- Regular log rotation
- Periodic configuration audits
- Keep blocklists updated
- Monitor system resources

## Troubleshooting

### Common Issues

1. **Module not found**: Ensure our enhanced pihole6api fork is installed in the correct Python environment
2. **Authentication errors**: Verify Pi-hole password and URL
3. **Connection timeouts**: Check network connectivity and Pi-hole service status
4. **Permission errors**: Ensure Pi-hole API is enabled and accessible

### Debug Mode

Enable debug output for troubleshooting:

```yaml
- name: Debug Pi-hole connection
  metrics:
    url: "{{ pihole_url }}"
    password: "{{ pihole_password }}"
    metric_type: "summary"
  register: result
  failed_when: false
  
- name: Show debug info
  debug:
    var: result
```

## Documentation

- Module documentation: `ansible-doc <module_name>`
- Role documentation: Available in each role's `README.md`
- API Reference: [pihole6api documentation](https://github.com/oriolrius/pihole6api/blob/main/docs/API_REFERENCE.md)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.