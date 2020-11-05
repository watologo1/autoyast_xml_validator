#!/bin/bash

# "SLE-15-Installer-LATEST" "SLE-15-SP1-Installer-LATEST" not listed, as they don't include a yast2-schema.
# TODO: support those versions in `generate_yast2_schema.sh` to get the necessary rng schema to use here.
distros=("SLE-12-SP4-Server-LATEST" "SLE-12-SP5-Server-LATEST" "SLE-15-SP2-Full-LATEST" "SLE-15-SP3-Full-LATEST" "openSUSE-Leap-15.1" "openSUSE-Leap-15.2" "openSUSE-Tumbleweed")
TEST_MACHINE="gusto.orthos_test.suse.de"
COBBLER_SERVER="10.162.227.30"  # smallfry
for distro in "${distros[@]}"; do
  ssh root@"${COBBLER_SERVER}" "cobbler system edit --profile=\"x86_64:${distro}-install-auto\" --name=\"${TEST_MACHINE}\""
  python3 validate-autoyastxml.py --cobbler "${COBBLER_SERVER}" --profile "yast2_schema/yast2-schema_${distro}/rng/profile.rng" --machine "${TEST_MACHINE}"
done
