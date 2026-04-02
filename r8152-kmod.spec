# Build only the akmod package and no kernel module packages:
%define buildforkernels akmod

%global debug_package %{nil}

Name:           r8152-kmod
Version:        2.21.4
Release:        1%{?dist}
Summary:        Linux kernel driver for realtek r81xx usb network adapters
License:        GPLv2
URL:            https://github.com/wget/realtek-r8152-linux

Source:         %{url}/archive/refs/heads/master.tar.gz
Patch0:          https://raw.githubusercontent.com/sisxph/r8152-kmod/refs/heads/main/Makefile.patch
# Get the needed BuildRequires (in parts depending on what we build for):
BuildRequires:  kmodtool

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Linux kernel driver for realtek r81xx usb network adapters

%prep
# Error out if there was something wrong with kmodtool:
%{?kmodtool_check}
# Print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%autosetup  -v realtek-r8152-linux-master
%patch -P0

for kernel_version in %{?kernel_versions}; do
    mkdir -p _kmod_build_${kernel_version%%___*}
    cp -a 50-usb-realtek-net.rules compatibility.h Makefile r8152.c _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}/
        make KERNELVER=${kernel_version%%___*} modules
    popd
done

%install
for kernel_version in %{?kernel_versions}; do
    mkdir -p %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
	install -m 0755 _kmod_build_${kernel_version%%___*}/*.ko %{buildroot}/%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
done
%{?akmod_install}

%changelog
