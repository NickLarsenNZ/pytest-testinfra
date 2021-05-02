# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import string
from testinfra.backend import base


class AciBackend(base.BaseBackend):
    NAME = "aci"

    def __init__(self, name, *args, **kwargs):
        # Must have a elft side and right side separated by @ with no whitespace
        if not ("@" in name or len(name) >= 3) or (True in [char in name for char in string.whitespace]):
            raise ValueError(
                f"aci container group must be specified with the resource group, eg containerGroupName@resourceGroupName. Got {name}")
        self.container_group, self.resource_group = name.split("@", 1)
        self.container = kwargs.get("container")
        super().__init__(name, *args, **kwargs)

    def run(self, command, *args, **kwargs):
        cmd = self.get_command(command, *args)

        azcmd = "az container exec --resource-group '%s' --name '%s' "
        azcmd_args = [self.resource_group, self.container_group]

        if self.container is not None:
            azcmd += "--container-name '%s' "
            azcmd_args.append(self.container)
        azcmd += "--exec-command %s"
        azcmd_args.extend([cmd])
        out = self.run_local(azcmd, *azcmd_args)
        return out
