# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Super simple fake memcache client."""

from nova.openstack.common import timeutils


class Client(object):
    """Replicates a tiny subset of memcached client interface."""

    def __init__(self, *args, **kwargs):
        """Ignores the passed in args."""
        self.cache = {}

    def get(self, key):
        """Retrieves the value for a key or None.

        this expunges expired keys during each get"""

        for k in self.cache.keys():
            (timeout, _value) = self.cache[k]
            if timeout and timeutils.utcnow_ts() >= timeout:
                del self.cache[k]

        return self.cache.get(key, (0, None))[1]

    def set(self, key, value, time=0, min_compress_len=0):
        """Sets the value for a key."""
        timeout = 0
        if time != 0:
            timeout = timeutils.utcnow_ts() + time
        self.cache[key] = (timeout, value)
        return True

    def add(self, key, value, time=0, min_compress_len=0):
        """Sets the value for a key if it doesn't exist."""
        if not self.get(key) is None:
            return False
        return self.set(key, value, time, min_compress_len)

    def incr(self, key, delta=1):
        """Increments the value for a key."""
        value = self.get(key)
        if value is None:
            return None
        new_value = int(value) + delta
        self.cache[key] = (self.cache[key][0], str(new_value))
        return new_value

    def delete(self, key, time=0):
        """Deletes the value associated with a key."""
        if key in self.cache:
            del self.cache[key]
