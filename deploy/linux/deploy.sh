#!/bin/bash

cd deploy/linux

# Remove previous images
rm passhfiles-*-x86_64.AppImage*

# Run app builder
appimage-builder