#!/bin/sh

cleanup () {
  [ -d ./cinema_lib ] && rm -rf ./cinema_lib
  exit 1
}

does_command_exist () {
  if ! command -v "$1" >/dev/null 2>&1; then
    if [ ! -z $2 ]; then
      echo "$1 was not found. Checking for $2..."
      sleep 1
      if ! command -v "$2" >/dev/null 2>&1; then
        echo "$1 and $2 were not found. At least one must be installed and added to your \$PATH"
        sleep 1
        cleanup
      else
        echo "$2 was found. Using $2..."
        sleep 1
        alias $1=$2
      fi
    else
      echo "$1 is not installed. It must be installed and added to your \$PATH"
      sleep1
      cleanup
    fi
  fi
}

check_version () {
  if [ "$2" != "" ]; then
    if echo $2 $3 | awk '{ exit ($1 >= $2) }'; then
      echo "$1 of at least version $3 is needed. $2 is currently installed."
      sleep 1
      cleanup
    fi
  else
    echo "$1 version could not be found. Check if it is installed."
    echo "pip install $1 OR pip3 install $1"
    sleep 1
    cleanup
  fi
}

clone_cinema_lib () {
  echo "Cloning cinema_lib repository..."
  git clone -q https://github.com/cinemascience/cinema_lib.git
  cd cinema_lib
}

install_cinema_lib () {
  echo "Installing..."
  pip install . >/dev/null 2>&1
  if ./cinema 2>/dev/null >/dev/null; then
    echo "cinema_lib successfully installed! To use it:"
    echo "cd `pwd`"
    echo "./cinema"
  else
    echo "cinema_lib was not successfully installed!"
    echo "Here is the error. Consider submitting an issue to ${github_page}"
    ./cinema
    cd ../
    cleanup
  fi
}

# Variables
github_page="https://github.com/cinemascience/cinema_lib"

# Check for existing cinema_lib
if [ -d ./cinema_lib ]; then
  echo "Looks like cinema_lib is already installed here!"
  echo "If you want to reinstall, move to a new install location or remove `pwd`/cinema_lib"
  exit 1
fi

# Check for Python 3.6
does_command_exist python3
does_command_exist pip pip3
check_version python "`python3 -c 'import sys; print(sys.version)' | awk 'NR==1' | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+).*/\1/g'`" 3.6

# Check for Numpy 1.13
check_version numpy "`python3 -c 'import numpy; print(numpy.__version__)' 2>/dev/null | awk 'NR==1' | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+).*/\1/g'`" 1.13

# Check for SciKit-Image 0.13.1
check_version scikit-image "`python3 -c 'import skimage; print(skimage.__version__)' 2>/dev/null | awk 'NR==1' | sed -E 's/([0-9]+\.[0-9]+\.[0-9]+).*/\1/g'`" 0.13.1

# Git clone cinema_lib
does_command_exist git
clone_cinema_lib

# Install cinema_lib
install_cinema_lib
