%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%global with_systemd 1
%else
%global with_systemd 0
%endif

Name: shine
Summary: Lustre administration utility
Version: %{version}
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.gz
License: GPL
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
BuildArchitectures: noarch
Requires: clustershell >= 1.5.1
%if %{with_systemd}
BuildRequires: systemd-units
%endif
Vendor: CEA
Url: http://lustre-shine.sourceforge.net/

%description
Lustre administration utility.

%prep
%setup

%build
python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/shine/models
cp conf/*.conf* $RPM_BUILD_ROOT/%{_sysconfdir}/shine
cp conf/ha.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/shine
cp conf/models/* $RPM_BUILD_ROOT/%{_sysconfdir}/shine/models
# man pages
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/{man1,man5}
gzip -c doc/shine.1 >$RPM_BUILD_ROOT/%{_mandir}/man1/shine.1.gz
gzip -c doc/shine.conf.5 >$RPM_BUILD_ROOT/%{_mandir}/man5/shine.conf.5.gz

%if %{with_systemd}
install -p -D -m 644 scripts/shine-ha.service %{buildroot}%{_unitdir}/shine-ha.service
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%config(noreplace) %{_sysconfdir}/shine/*.conf
%config(noreplace) %{_sysconfdir}/shine/ha.yaml
%config %{_sysconfdir}/shine/*.conf.example
%config %{_sysconfdir}/shine/models/*.lmf
%doc LICENSE README ChangeLog
%doc %{_mandir}/man1/shine.1.gz
%doc %{_mandir}/man5/shine.conf.5.gz
%if %{with_systemd}
%{_unitdir}/shine-ha.service
%endif

%changelog
* Sun Feb  5 2017 <sthiell@stanford.edu> - 1.4-2
- Update from oak_ha branch at Stanford
- Add shine-ha.service

* Wed Apr 29 2015 <aurelien.degremont@cea.fr> - 1.4-1
- Update to shine 1.4

* Tue Mar 11 2014 <aurelien.degremont@cea.fr> - 1.3.1-1
- Update to shine 1.3.1

* Thu Oct 10 2013 <aurelien.degremont@cea.fr> - 1.3-1
- Update to shine 1.3
