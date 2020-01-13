#!/bin/sh -x

# Checks that need to happen:
# [ ] Does command exist
# [ ] Does python have everything needed? Find binary, version >= 3.6
# [ ] scikit-image >= 0.13.1 (Optional)
# [ ] opencv-python >= 3.4 (Optional)

does_command_exist () {
  if ! command -v "$@" >/dev/null 2>&1; then
    echo "$1 is not installed. It must be installed and added to your \$PATH"
    exit 1
  fi
}

check_version () {
  if echo $2 $3 | awk '{ exit ($1 >= $2) }'; then
    echo "$1 of at least version $3 is needed"
    exit 1
  fi
}

clone_cinema_lib () {
  does_command_exist git

  git clone https://github.com/cinemascience/cinema_lib.git
  cd cinema_lib
}

install_cinema_lib () {
  does_command_exist pip
  pip install . >/dev/null 2>&1
}

# Variables

# Main

# Check for Python 3.6
does_command_exist python3
check_version python `python3 -c 'import sys; print(sys.version)' | awk 'NR==1' | sed 's/\([0-9]\.[0-9]\).*/\1/g'` 3.6

# Check for Numpy 1.13
check_version numpy `python3 -c 'import numpy; print(numpy.__version__)' | awk 'NR==1' | sed 's/\([0-9]\.[0-9]+\)\..*/\1/g'` 1.13

# Git clone cinema_lib
clone_cinema_lib

# Install cinema_lib
install_cinema_lib
