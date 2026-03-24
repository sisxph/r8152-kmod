# Define the kmod package name here.
%define kmod_name r8152


# (un)define the next line to either build for the newest or all current kernels
%define buildforkernels newest
%define buildforkernels current
%define buildforkernels akmod






# name should have a -kmod suffix
Name:    %{kmod_name}-kmod
Version: 2.21.4
Release: 1%{?dist}
Summary: %{kmod_name} kernel module(s)

Group:          System Environment/Kernel

License: GPLv2
URL:     http://www.realtek.com.tw/

# Sources.
Source0:  realtek-%{kmod_name]-%{version}.tar.gz
Source10: kmodtool-%{kmod_name}.sh
Source20: Repo-Makefile-%{kmod_name}
Patch0:  %{kmod_name}.patch
Patch1:  %{kmod_name}-h.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  %{_bindir}/kmodtool
BuildRequires: perl
BuildRequires: redhat-rpm-config


# get the proper build-sysbuild package from the repo, which
# tracks in all the kernel-devel packages
BuildRequires:  %{_bindir}/kmodtool
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


%description
This package provides the %{kmod_name} kernel module(s).
It is built to depend upon the specific ABI provided by a range of releases
of the same variant of the Linux kernel and not on any one specific build.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -n %{kmod_name}-%{version}
rm -f Makefile*
cp -a %{SOURCE20} Makefile
echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf

# %patch0 -p0
# %patch1 -p0

for kernel_version in %{?kernel_versions} ; do
    cp -a %{kmod_name}-%{version} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${kernel_version##*___}" SUBDIRS=${PWD}/_kmod_build_${kernel_version%%___*} modules
done

%install
rm -rf ${RPM_BUILD_ROOT}

for kernel_version in %{?kernel_versions}; do
    make install DESTDIR=${RPM_BUILD_ROOT} KMODPATH=%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
    # install -D -m 755 _kmod_build_${kernel_version%%___*}/%{kmod_name}/%{kmod_name}.ko  ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/%{kmod_name}.ko
done
%{?akmod_install}


%{__install} -d ${RPM_BUILD_ROOT}/lib/modules/${kernel_version%%___*}/extra/%{kmod_name}/
%{__install} %{kmod_name}.ko ${RPM_BUILD_ROOT}/lib/modules/${kernel_version%%___*}/extra/%{kmod_name}/
%{__install} -d ${RPM_BUILD_ROOT}%{_sysconfdir}/depmod.d/
%{__install} kmod-%{kmod_name}.conf ${RPM_BUILD_ROOT}%{_sysconfdir}/depmod.d/
%{__install} -d ${RPM_BUILD_ROOT}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
%{__install} -d ${RPM_BUILD_ROOT}%{_sysconfdir}/udev/rules.d/
#%{__install} 50-usb-realtek-net.rules ${RPM_BUILD_ROOT}%{_sysconfdir}/udev/rules.d/
%{__install} ReadMe.txt ${RPM_BUILD_ROOT}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/

# strip the modules(s)
find "${RPM_BUILD_ROOT}" -type f -name '*.ko' -exec %{__strip} --strip-debug '{}' \;


# Sign the modules(s)
%if %{?_with_modsign:1}%{!?_with_modsign:0}
# If the module signing keys are not defined, define them here.
%{!?privkey: %define privkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.priv}
%{!?pubkey: %define pubkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.der}
for module in $(find ${RPM_BUILD_ROOT} -type f -name \*.ko);
do %{__perl} /usr/src/kernels/${kernel_version%%___*}/scripts/sign-file \
sha256 %{privkey} %{pubkey} $module;
done
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Oct 05 2015 Philip J Perry <phil@elrepo.org> - 7.0-1
- Initial el7 build of the kmod package.
- Backported from kernel-3.10.90
