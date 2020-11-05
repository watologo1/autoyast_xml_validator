#!/bin/bash

DEBUG=0
ARCH="x86_64"
DISTROS="SLE-12-SP4-Server-LATEST/$ARCH/DVD1/suse/$ARCH SLE-12-SP5-Server-LATEST/$ARCH/DVD1/suse/$ARCH SLE-15-SP2-Full-LATEST/$ARCH/DVD1/Module-Basesystem/x86_64 SLE-15-SP3-Full-LATEST/$ARCH/DVD1/Module-Basesystem/x86_64 openSUSE-Leap-15.1/$ARCH/DVD1/$ARCH openSUSE-Leap-15.2/$ARCH/DVD1/$ARCH openSUSE-Tumbleweed/$ARCH/DVD1/$ARCH"
#DISTROS="SLE-12-SP4-Server-LATEST/$ARCH/DVD1/suse/$ARCH SLE-12-SP5-Server-LATEST/$ARCH/DVD1/suse/$ARCH SLE-15-Installer-LATEST/$ARCH/DVD1/$ARCH SLE-15-SP1-Installer-LATEST/$ARCH/DVD1/Module-Basesystem/x86_64 SLE-15-SP2-Full-LATEST/$ARCH/DVD1/Module-Basesystem/x86_64 SLE-15-SP3-Full-LATEST/$ARCH/DVD1/Module-Basesystem/x86_64 openSUSE-Leap-15.1/$ARCH/DVD1/$ARCH openSUSE-Leap-15.2/$ARCH/DVD1/$ARCH openSUSE-Tumbleweed/$ARCH/DVD1/$ARCH"
#DISTROS="SLE-15-SP3-Full-LATEST/$ARCH/DVD1/Module-Basesystem/x86_64 SLE-15-SP2-Full-LATEST/$ARCH/DVD1/Module-Basesystem/x86_64 SLE-12-SP5-Server-LATEST/$ARCH/DVD1/suse/$ARCH SLE-12-SP4-Server-LATEST/$ARCH/DVD1/suse/$ARCH openSUSE-Tumbleweed/$ARCH/DVD1/$ARCH openSUSE-Leap-15.2/$ARCH/DVD1/$ARCH"
OUTPUT_DIR="yast2_schema"

if [[ DEBUG -eq 1 ]];then
    for x in $DISTROS;do
	if ! [ -e "/mounts/dist/install/SLP/${x}"/yast2-schema*.rpm ];then
	    echo "Did not find $x"
	else
	    ls /mounts/dist/install/SLP/"${x}"/yast2-schema*.rpm
	fi
    done
    exit 0
fi

B_URL="ftp://dist.suse.de/install/SLP"

TMP=$(mktemp -d)

function err_out
{
    echo "ERROR: $1"
    exit 1
}

for DISTRO in $DISTROS;do
    RPM_URL="${B_URL}/${DISTRO}/yast2-schema*.rpm"
    BASE=${DISTRO%%/*}
    echo $BASE
    tmp_dir="${TMP}/yast2-schema_${BASE}"
    mkdir "$tmp_dir" >/dev/null
    pushd "$tmp_dir" >/dev/null
    if wget -q "$RPM_URL";then
	! [ -e *.rpm ] && err_out "Could not retrieve yast2-schema rpm from $RPM_URL"
	cat *.rpm | rpm2cpio - >rpm_unpacked 
	if unzstd --quiet --test rpm_unpacked 2>/dev/null;then
	    cat rpm_unpacked |unzstd --quiet -| cpio --quiet -i --make-directories --preserve-modification-time *.rng
	else
	    cat rpm_unpacked |cpio --quiet -i --make-directories --preserve-modification-time *.rng
	fi
	rm rpm_unpacked
	! [ -d usr/share/YaST2/schema/autoyast/rng ] && err_out "Could not unpack rpm " *.rpm
	mv usr/share/YaST2/schema/autoyast/rng .
	rm -rf usr/
    else
	echo "URL not valid: $RPM_URL"
	exit 1
    fi
    popd >/dev/null
done
if [ -e "${OUTPUT_DIR}" ];then
    echo "${OUTPUT_DIR} already exits"
    echo "Schema files are located here:"
    echo "${TMP}"
else
    set -x
    mv "${TMP}" "${OUTPUT_DIR}"
    set +x
fi

