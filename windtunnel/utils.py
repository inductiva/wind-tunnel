""""This module contains utility functions for the Windtunnel application. """

from typing import Optional

import inductiva


def get_number_subdomains(machine_group: inductiva.resources.MachineGroup):
    """Returns the number of subdomains based on the machine group.
    We halve the number of vCPUs to determine the number of subdomains.

    Args:
        machine_group: The machine group to determine the number of subdomains.
    """

    if machine_group is None:
        return 4  # Number of subdomains for the default machine group
    num_vcpus = int(machine_group.machine_type.split("-")[-1])
    num_subdomains = num_vcpus // 2
    return num_subdomains


def get_machine_group(machine_group_name: Optional[str] = None):
    """Returns the machine group based on the provided name.

    Args:
        machine_group_name: Name of the machine group. If not provided, the
            default machine group will be returned.
    """
    if machine_group_name is None:
        return None
    mg = inductiva.resources.machine_groups.get_by_name(machine_group_name)
    return mg
