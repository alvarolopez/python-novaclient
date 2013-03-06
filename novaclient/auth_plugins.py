# Copyright 2011 OpenStack LLC.
# Copyright 2013 Spanish National Research Council.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pkg_resources
import logging

from novaclient import exceptions


def get_auth_system_url(auth_system):
    """Load plugin-based auth_url."""
    ep_name = 'openstack.client.auth_url'
    for ep in pkg_resources.iter_entry_points(ep_name):
        if ep.name == auth_system:
            return ep.load()()
    raise exceptions.AuthSystemNotFound(auth_system)


def discover_auth_system_opts(parser):
    """Discover options needed by the available auth-system.

    This function will call all the entry points
    "openstack.client.add_auth_opts" so that the available auth systems can
    populate its options to the parser.
    """
    ep_name = 'openstack.client.add_auth_opts'
    for ep in pkg_resources.iter_entry_points(ep_name):
        try:
            # Catch any exceptions to prevent from misconfigured auth-systems
            f = ep.load()
        except:
            pass
        else:
            group = parser.add_argument_group("Auth-system '%s' options" %
                    ep.name)
            f(group)


def parse_auth_system_opts(auth_system, args):
    """Parse the actual auth-system options if any.

    This function will call the entry point "openstack.client.parse_auth_opts"
    for the selected auth system. This function is expected to return a dict
    with all the options that it needs to perform authentication. If the dict
    is empty or if the entry point doest not exist, we assume that it needs
    the same options as the 'keystone' auth system.
    """
    ep_name = 'openstack.client.parse_auth_opts'
    for ep in pkg_resources.iter_entry_points(ep_name):
        if ep.name == auth_system:
            return ep.load()(args)
    return None


def plugin_auth(cls, auth_url):
    """Load plugin-based authentication."""
    ep_name = 'openstack.client.authenticate'
    for ep in pkg_resources.iter_entry_points(ep_name):
        if ep.name == cls.auth_system:
            return ep.load()(cls, auth_url)
    raise exceptions.AuthSystemNotFound(cls.auth_system)
