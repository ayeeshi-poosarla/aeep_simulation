#!/bin/bash

set -e

echo "[1/7] Updating system..."
sudo apt update && sudo apt upgrade -y

echo "[2/7] Installing required dependencies..."
sudo apt install -y git cmake build-essential \
    libxt-dev libxrender-dev libxext-dev qtbase5-dev \
    qttools5-dev qttools5-dev-tools libgl1-mesa-dev \
    libglu1-mesa-dev libjpeg-dev libpng-dev \
    python3-dev python3-pip python3-numpy python3-venv \
    libtbb-dev swig

echo "[3/7] Setting up swap space (2GB)..."
sudo dphys-swapfile swapoff
sudo sed -i 's/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

echo "[4/7] Cloning VTK source (v9.2.6)..."
cd ~
git clone https://gitlab.kitware.com/vtk/vtk.git
cd vtk
git checkout v9.2.6

echo "[5/7] Building VTK..."
mkdir build && cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DVTK_WRAP_PYTHON=ON \
  -DVTK_PYTHON_VERSION=3 \
  -DPython3_EXECUTABLE=$(which python3) \
  -DBUILD_TESTING=OFF \
  -DVTK_GROUP_ENABLE_Qt=NO

make -j$(nproc)

echo "[6/7] Installing VTK..."
sudo make install
sudo ldconfig

echo "[7/7] Verifying installation..."
python3 -c "import vtk; print('VTK version:', vtk.vtkVersion().GetVTKVersion())"

echo "✅ VTK successfully installed with Python bindings!"
