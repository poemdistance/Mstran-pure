#!/bin/bash

meson setup builddir
cd builddir 
ninja
sudo meson install
sudo cp -v src/gnome-screenshot /usr/bin
