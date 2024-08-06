#!/usr/bin/bash
working_dir_name=~/tpms_lab

# remove the previous student's lab
rm -rf $working_dir

# create a new directory with all the contents of this one
mkdir -p $working_dir
cp -r . $working_dir

# remove the install and refresh scripts
rm $working_dir/install.sh
rm $working_dir/refresh.sh
