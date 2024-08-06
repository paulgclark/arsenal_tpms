#!/usr/bin/bash
# this script installs the software required for this lab on Debian machines

# install uhd drivers
sudo apt -y install libuhd-dev

# install gnuradio
sudo apt -y install gnuradio-dev

# install gr-satellites
sudo apt -y install gr-satellites
