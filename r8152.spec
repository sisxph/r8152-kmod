%global modname r8152

%if 0%{?fedora}
%global debug_package %{nil}
%endif

Name:     %{modname}
Version:  2.21.4
Release:  1%{?dist}
Summary:  Linux kernel driver for realtek r81xx usb network adapters
License:  GPLv2
URL:      https://github.com/wget/realtek-r8152-linux
Source0:  %{url}/archive/refs/heads/master.tar.gz

Provides: %{name}-kmod-common = %{version}
Requires: %{name}-kmod >= %{version}

%description
Linux kernel driver for realtek r81xx usb network adapters

%prep
%autosetup -p1 -n realtek-r8152-linux-master


%install
mkdir -p %{buildroot}/usr/lib/udev/rules.d/
install -D -m 0644 50-usb-realtek-net.rules %{buildroot}/usr/lib/udev/rules.d/50-usb-realtek-net.rules
install -D -m 0644 LICENSE %{buildroot}%{_datarootdir}/licenses/%{name}/LICENSE

%files
%license LICENSE
%doc ReadMe.txt
/usr/lib/udev/rules.d/50-usb-realtek-net.rules

%changelog
