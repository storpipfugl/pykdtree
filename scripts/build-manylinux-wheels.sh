#!/bin/bash
set -e -x

# This is to be run by Docker inside a Docker image.
# You can test it locally on a Linux machine by installing docker and running from this repo's root:
# $ docker run -e PLAT=manylinux2010_x86_64 -v `pwd`:/io quay.io/pypa/manylinux2010_x86_64 /io/scripts/build-manylinux-wheels.sh

# * The -e just defines an environment variable PLAT=[docker name] inside the
#    docker - auditwheel can't detect the docker name automatically.
# * The -v gives a directory alias for passing files in and out of the docker
#    (/io is arbitrary). E.g the `setup.py` script would be accessed in the
#    docker via `/io/setup.py`.
# * quay.io/pypa/manylinux2010_x86_64 is the full docker image name. Docker
#    downloads it automatically.
# * The last argument is a shell command that the Docker will execute.
#    Filenames must be from the Docker's perspective.

# Wheels are initially generated as you would usually, but put in a temp
# directory temp-wheels. The pip-cache is optional but can speed up local builds
# having a real permanent pip-cache dir.
mkdir -p /io/pip-cache
mkdir -p /io/temp-wheels

# Clean out any old existing wheels.
find /io/temp-wheels/ -type f -delete

# Iterate through available pythons.
for PY in cp3{7,8,9,10}; do
    for PYBIN in /opt/python/"${PY}"*/bin; do
        "${PYBIN}/pip" install -q -U setuptools wheel pytest build --cache-dir /io/pip-cache
        # Run the following in root of this repo.
        pushd /io/
        USE_OMP=$USE_OMP "${PYBIN}/pip" install -q .
        USE_OMP=$USE_OMP "${PYBIN}/pytest" --pyargs pykdtree
        USE_OMP=$USE_OMP "${PYBIN}/python" -m build -w -o /io/temp-wheels
        popd
    done
done

"$PYBIN/pip" install -q auditwheel

# Wheels aren't considered manylinux unless they have been through
# auditwheel. Audited wheels go in /io/dist/.
mkdir -p /io/dist/

for whl in /io/temp-wheels/*.whl; do
    auditwheel repair "$whl" --plat "$PLAT" -w /io/dist/
done
