#!/bin/bash

# Create a debian package for dalyinski server
# https://senties-martinelli.com/articles/debian-packages
# https://stackoverflow.com/questions/1382569/how-do-i-do-debian-packaging-of-a-python-package

# exit immediatelly if some command below fails
set -e

if [[ -z $1 ]]
then
    echo "Usage sudo ./create_deb.sh <version>"
    exit 1

fi
TEMPLATE_DIR=debian-pkg/template
VERSION="$1"

OLD_VERSION=$(ls debian-pkg/ | awk -F\- '{ print $2 }')
APP_DIR=debian-pkg/dalyinski-${VERSION}
BINARY_SRC=dist/dalyinski-server
BINARY_DST=${APP_DIR}/usr/bin/

echo "[*] Update version string in .desktop, Debian control file and github workflow files"
sed -i "/Version/s/[[:digit:]]\+\.[[:digit:]]\+/${VERSION}/" ${TEMPLATE_DIR}/usr/share/applications/dalYinski.desktop
sed -i "/Version/s/[[:digit:]]\+\.[[:digit:]]\+/${VERSION}/" ${TEMPLATE_DIR}/DEBIAN/control
# sed -i "s/[[:digit:]]\+\.[[:digit:]]\+/${VERSION}/" .github/workflows/main.yml

echo "[*] Copy scripts to packaging dir"
if [[ ! -d ${APP_DIR}/usr/lib/python3/dist-packages/ ]]
then
    mkdir -p ${APP_DIR}/usr/lib/python3/dist-packages/
fi
cp -r ${TEMPLATE_DIR}/* ${APP_DIR}
cp -r dalyinski ${APP_DIR}/usr/lib/python3/dist-packages/
cp dalyinski-server.py ${APP_DIR}/usr/bin/dalyinski-server


# echo "[*] Building the binary..."
# source venv/bin/activate
# pyinstaller --onefile launch.py --name dalyinski-server

# echo "[*] Move built binary to debian-pkg folder"
# mv ${BINARY_SRC} debian-pkg/${BINARY_DST} 

echo "[*] Copy everything to /tmp"
sudo cp -r ${APP_DIR} /tmp

echo "[*] Change all the folder permission to root" 
sudo chown -R root:root /tmp/dalyinski-${VERSION}

echo "[*] Change the script's permissions to executable" 
sudo chmod 0755 /tmp/dalyinski-${VERSION}/usr/bin/dalyinski-server

echo "[*] Build the package" 
dpkg -b /tmp/dalyinski-${VERSION}

echo "[*] Move deb package to current folder"
mv /tmp/dalyinski-${VERSION}.deb ${PWD}

echo "[*] Cleanup"
if [[ -d /tmp/dalyinski-${VERSION} ]]
then
    sudo rm -rf /tmp/dalyinski-${VERSION}
fi

if [[ -d ${APP_DIR}/usr/lib/python3/dist-packages/dalyinski ]]
then
    rm -rf ${APP_DIR}/usr/lib/python3/dist-packages/dalyinski
fi
rm -rf ${APP_DIR}
