#!/usr/bin/bash
# this script installs the software required for this lab on Debian machines

# install uhd drivers
sudo apt -y install libuhd-dev
sudo apt -y install uhd-host
sudo uhd_images_downloader

# install gnuradio
sudo apt -y install gnuradio-dev

# install gr-satellites
sudo apt -y install gr-satellites
