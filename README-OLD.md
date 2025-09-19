# 🍓 pihole-ansible

This collection provides comprehensive Ansible modules and roles for managing Pi-hole v6 instances via the custom API client. This collection is built on top of the [pihole6api](https://github.com/sbarbett/pihole6api) Python library, which handles authentication and requests to Pi-hole's API.

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

## Getting Started

### Prerequisites

- **Ansible:** Version 2.9 or later.
- **Python:** The control node requires Python 3.x.
- **pihole6api Library**

### Installation

Install the collection via Ansible Galaxy:

```bash
ansible-galaxy collection install sbarbett.pihole
```

You can also build it locally:

```bash
git clone https://github.com/sbarbett/pihole-ansible
ansible-galaxy collection build
ansible-galaxy collection install sbarbett-pihole-x.x.x.tar.gz
```

#### `pihole6api` Dependency

The `pihole6api` library is required for this Ansible collection to function. The installation method depends on how you installed Ansible.

```bash
pip install pihole6api
```

However, some Linux distributions (Debian, macOS, Fedora, etc.) **restrict system-wide `pip` installs** due to [PEP 668](https://peps.python.org/pep-0668/). In that case, use one of the methods below.

**Installing in a Virtual Environment (Recommended):**

If you want an isolated environment that won’t interfere with system-wide packages, install both `pihole6api` and Ansible in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install pihole6api ansible
```

To confirm that `ansible` and `pihole6api` are installed correctly within the environment, run:

```bash
which python && which ansible
python -c "import pihole6api; print(pihole6api.__file__)"
```

To exit the virtual environment:

```bash
deactivate
```

**Using `pipx`:**

If Ansible is installed via `pipx`, inject `pihole6api` into Ansible’s environment:

```bash
pipx inject ansible pihole6api --include-deps
```

Verify installation:

```bash
pipx runpip ansible show pihole6api
```

Since Ansible does not automatically detect `pipx` environments, you must explicitly set the Python interpreter in your Ansible configuration:

Edit `ansible.cfg`:

```
[defaults]
interpreter_python = ~/.local/pipx/venvs/ansible/bin/python
```

For more information on `pipx` see [the official documentation](https://github.com/pypa/pipx) and [the Ansible install guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html).

**Installing for System-Wide Ansible (Generally Not Recommended):**

If Ansible was installed via a package manager (`apt`, `dnf`, `brew`) and a virtual environment or `pipx` is not a feasible or desired solution, run `pip` with `--break-system-packages` to bypass **PEP 668** restrictions:

```bash
sudo pip install --break-system-packages pihole6api
```

Verify installation:

```bash
python3 -c "import pihole6api; print(pihole6api.__file__)"

```

## Usage Examples

### Modules

* [Enable and Configure the PiHole DHCP Client](https://github.com/sbarbett/pihole-ansible/blob/main/examples/configure-dhcp-client.yml)
* [Disable the PiHole DHCP Client](https://github.com/sbarbett/pihole-ansible/blob/main/examples/disable-dhcp-client.yml)
* [Remove a DHCP Lease](https://github.com/sbarbett/pihole-ansible/blob/main/examples/remove-dhcp-lease.yml)
* [Create a Local A Record](https://github.com/sbarbett/pihole-ansible/blob/main/examples/create-a-record.yml)
* [Remove a Local A Record](https://github.com/sbarbett/pihole-ansible/blob/main/examples/delete-a-record.yml)
* [Create a Local CNAME](https://github.com/sbarbett/pihole-ansible/blob/main/examples/create-cname.yml)
* [Remove a Local CNAME](https://github.com/sbarbett/pihole-ansible/blob/main/examples/delete-cname.yml)
* [Create an Allow List](https://github.com/sbarbett/pihole-ansible/blob/main/examples/create-allow-list.yml)
* [Create a Block List](https://github.com/sbarbett/pihole-ansible/blob/main/examples/create-block-list.yml)
* [Manage Allow Lists](https://github.com/sbarbett/pihole-ansible/blob/main/examples/manage-allow-lists.yml)
* [Manage Block Lists](https://github.com/sbarbett/pihole-ansible/blob/main/examples/manage-block-lists.yml)
* [Manage Groups](https://github.com/sbarbett/pihole-ansible/blob/main/examples/manage-groups.yml)
* [Manage Clients](https://github.com/sbarbett/pihole-ansible/blob/main/examples/manage-clients.yml)

### Roles

Roles are designed to orchestrate changes across multiple PiHole instances.

* [Manage Local Records](https://github.com/sbarbett/pihole-ansible/blob/main/examples/manage-records.yml)
* [Manage Lists](https://github.com/sbarbett/pihole-ansible/blob/main/examples/manage-lists.yml)
* [Manage Groups and Clients](https://github.com/sbarbett/pihole-ansible/blob/main/examples/manage-groups-clients.yml)

## Documentation

* Each module includes embedded documentation. You can review the options by using `ansible-doc sbarbett.module_name`.
* Detailed information for each role is provided in its own `README` file within the role directory.

## License

MIT
