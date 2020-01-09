%if 0%{?fedora} > 27
%global py2_prefix python2
%else
%global py2_prefix python
%endif

Name: criu
Version: 3.5
Release: 4%{?dist}
Provides: crtools = %{version}-%{release}
Obsoletes: crtools <= 1.0-2
Summary: Tool for Checkpoint/Restore in User-space
Group: System Environment/Base
License: GPLv2
URL: http://criu.org/
Source0: http://download.openvz.org/criu/criu-%{version}.tar.bz2
Patch0: 0001-fix-building-on-newest-glibc-and-kernel.patch

%if ! 0%{?fedora}
BuildRequires: perl
# RHEL has no asciidoc; take man-page from Fedora 26
# zcat /usr/share/man/man8/criu.8.gz > criu.8
Source1: criu.8
Source2: crit.1
# The patch aio-fix.patch is needed as RHEL7
# doesn't do "nr_events *= 2" in ioctx_alloc().
Patch100: aio-fix.patch
%endif

Source3: criu-tmpfiles.conf

BuildRequires: systemd
BuildRequires: libnet-devel
BuildRequires: protobuf-devel protobuf-c-devel python2-devel libnl3-devel libcap-devel
%if 0%{?fedora}
BuildRequires: asciidoc xmlto
BuildRequires: perl-interpreter
%endif

# user-space and kernel changes are only available for x86_64, arm,
# ppc64le, aarch64 and s390x
# https://bugzilla.redhat.com/show_bug.cgi?id=902875
ExclusiveArch: x86_64 %{arm} ppc64le aarch64 s390x

%description
criu is the user-space part of Checkpoint/Restore in User-space
(CRIU), a project to implement checkpoint/restore functionality for
Linux in user-space.

%if 0%{?fedora}
%package devel
Summary: Header files and libraries for %{name}
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
This package contains header files and libraries for %{name}.
%endif

%package -n %{py2_prefix}-%{name}
%{?python_provide:%python_provide %{py2_prefix}-%{name}}
Summary: Python bindings for %{name}
Group: Development/Languages
Requires: %{name} = %{version}-%{release} python-ipaddr protobuf-python

%description -n %{py2_prefix}-%{name}
python-%{name} contains Python bindings for %{name}.

%package -n crit
Summary: CRIU image tool
Requires: %{py2_prefix}-%{name} = %{version}-%{release}

%description -n crit
crit is a tool designed to decode CRIU binary dump files and show
their content in human-readable form.


%prep
%setup -q
%patch0 -p1

%if 0%{?rhel}
%patch100 -p1
%endif

%build
# %{?_smp_mflags} does not work
# -fstack-protector breaks build
CFLAGS+=`echo %{optflags} | sed -e 's,-fstack-protector\S*,,g'` make V=1 WERROR=0 PREFIX=%{_prefix} RUNDIR=/run/criu
%if 0%{?fedora}
make docs V=1
%endif


%install
make install-criu DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir}
make install-lib DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir}
%if 0%{?fedora}
# only install documentation on Fedora as it requires asciidoc,
# which is not available on RHEL7
make install-man DESTDIR=$RPM_BUILD_ROOT PREFIX=%{_prefix} LIBDIR=%{_libdir}
%else
install -p -m 644  -D %{SOURCE1} $RPM_BUILD_ROOT%{_mandir}/man8/%{name}.8
install -p -m 644  -D %{SOURCE2} $RPM_BUILD_ROOT%{_mandir}/man1/crit.1
%endif

mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 0644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -d -m 0755 %{buildroot}/run/%{name}/

%if ! 0%{?fedora}
# remove devel package
rm -rf $RPM_BUILD_ROOT%{_includedir}/criu
rm $RPM_BUILD_ROOT%{_libdir}/*.so*
rm -rf $RPM_BUILD_ROOT%{_libdir}/pkgconfig
rm -rf $RPM_BUILD_ROOT%{_libexecdir}/%{name}
%endif

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_sbindir}/%{name}
%doc %{_mandir}/man8/criu.8*
%if 0%{?fedora}
%{_libdir}/*.so.*
%{_libexecdir}/%{name}
%endif
%dir /run/%{name}
%{_tmpfilesdir}/%{name}.conf
%doc README.md COPYING

%if 0%{?fedora}
%files devel
%{_includedir}/criu
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%endif

%files -n %{py2_prefix}-%{name}
%{python2_sitelib}/pycriu/*
%{python2_sitelib}/*egg-info

%files -n crit
%{_bindir}/crit
%doc %{_mandir}/man1/crit.1*


%changelog
* Tue Oct 10 2017 Adrian Reber <areber@redhat.com> - 3.5-4
- Upgrade imported manpages to 3.5

* Mon Oct 09 2017 Adrian Reber <areber@redhat.com> - 3.5-3
- Fix ExclusiveArch on RHEL

* Mon Oct 02 2017 Adrian Reber <adrian@lisas.de> - 3.5-2
- Merge RHEL and Fedora spec file

* Thu Sep 28 2017 Adrian Reber <adrian@lisas.de> - 3.5-1
- Update to 3.5 (#1496614)

* Sun Aug 27 2017 Adrian Reber <adrian@lisas.de> - 3.4-1
- Update to 3.4 (#1483774)
- Removed upstreamed patches
- Added s390x (#1475719)

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.3-5
- Python 2 binary package renamed to python2-criu
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 20 2017 Adrian Reber <adrian@lisas.de> - 3.3-2
- Added patches to handle changes in glibc

* Wed Jul 19 2017 Adrian Reber <adrian@lisas.de> - 3.3-1
- Update to 3.3

* Fri Jun 30 2017 Adrian Reber <adrian@lisas.de> - 3.2.1-2
- Added patches to handle unified hierarchy and new glibc

* Wed Jun 28 2017 Adrian Reber <adrian@lisas.de> - 3.2.1-1
- Update to 3.2.1-1

* Wed Jun 28 2017 Adrian Reber <areber@redhat.com> - 2.12-2
- Added patches for guard page kernel fixes

* Thu Mar 09 2017 Adrian Reber <adrian@lisas.de> - 2.12-1
- Update to 2.12

* Fri Feb 17 2017 Adrian Reber <adrian@lisas.de> - 2.11.1-1
- Update to 2.11.1

* Thu Feb 16 2017 Adrian Reber <adrian@lisas.de> - 2.11-1
- Update to 2.11

* Mon Feb 13 2017 Adrian Reber <adrian@lisas.de> - 2.10-4
- Added patch to fix build on ppc64le

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 23 2017 Orion Poplawski <orion@cora.nwra.com> - 2.10-2
- Rebuild for protobuf 3.2.0

* Mon Jan 16 2017 Adrian Reber <adrian@lisas.de> - 2.10-1
- Update to 2.10

* Mon Dec 12 2016 Adrian Reber <adrian@lisas.de> - 2.9-1
- Update to 2.9
- Added crit manpage to crit subpackage

* Tue Jun 14 2016 Adrian Reber <areber@redhat.com> - 2.3-2
- Added patches to handle in-flight TCP connections

* Tue Jun 14 2016 Adrian Reber <areber@redhat.com> - 2.3-1
- Update to 2.3
- Copy man-page from Fedora 24 for RHEL

* Mon May 23 2016 Adrian Reber <adrian@lisas.de> - 2.2-1
- Update to 2.2

* Tue Apr 12 2016 Adrian Reber <adrian@lisas.de> - 2.1-2
- Remove crtools symbolic link

* Mon Apr 11 2016 Adrian Reber <adrian@lisas.de> - 2.1-1
- Update to 2.1

* Fri Apr 08 2016 Adrian Reber <areber@redhat.com> - 2.0-3
- Exclude arm and aarch64 from build

* Wed Apr 06 2016 Adrian Reber <areber@redhat.com> - 2.0-2
- Merge changes from Fedora

* Thu Mar 10 2016 Andrey Vagin <avagin@openvz.org> - 2.0-1
- Update to 2.0

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 07 2015 Adrian Reber <adrian@lisas.de> - 1.8-1
- Update to 1.8

* Mon Nov 02 2015 Adrian Reber <adrian@lisas.de> - 1.7.2-1
- Update to 1.7.2

* Mon Sep 7 2015 Andrey Vagin <avagin@openvz.org> - 1.7-1
- Update to 1.7

* Mon Aug 31 2015 Adrian Reber <areber@redhat.com> - 1.6.1-3
- added patch to fix broken docker checkpoint/restore (#1258539)

* Fri Aug 28 2015 Adrian Reber <areber@redhat.com> - 1.6.1-2
- removed criu.service (CVE-2015-5228, CVE-2015-5231)
- removed devel sub-package (related to above CVEs)

* Wed Aug 19 2015 Adrian Reber <areber@redhat.com> - 1.6.1-1.1
- fix release version number

* Thu Aug 13 2015 Adrian Reber <adrian@lisas.de> - 1.6.1-1
- Update to 1.6.1
- Merge changes for RHEL packaging

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 09 2015 Adrian Reber <areber@redhat.com> - 1.6-1.1
- adapt to RHEL7

* Mon Jun 01 2015 Andrew Vagin <avagin@openvz.org> - 1.6-1
- Update to 1.6

* Thu Apr 30 2015 Andrew Vagin <avagin@openvz.org> - 1.5.2-2
- Require protobuf-python and python-ipaddr for python-criu

* Tue Apr 28 2015 Andrew Vagin <avagin@openvz.org> - 1.5.2
- Update to 1.5.2

* Sun Apr 19 2015 Nikita Spiridonov <nspiridonov@odin.com> - 1.5.1-2
- Create python-criu and crit subpackages

* Tue Mar 31 2015 Andrew Vagin <avagin@openvz.org> - 1.5.1
- Update to 1.5.1

* Sat Dec 06 2014 Adrian Reber <adrian@lisas.de> - 1.4-1
- Update to 1.4

* Tue Sep 23 2014 Adrian Reber <adrian@lisas.de> - 1.3.1-1
- Update to 1.3.1 (#1142896)

* Tue Sep 02 2014 Adrian Reber <adrian@lisas.de> - 1.3-1
- Update to 1.3
- Dropped all upstreamed patches
- included pkgconfig file in -devel

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Aug 07 2014 Andrew Vagin <avagin@openvz.org> - 1.2-4
- Include inttypes.h for PRI helpers

* Thu Aug 07 2014 Andrew Vagin <avagin@openvz.org> - 1.2-3
- Rebuilt for https://bugzilla.redhat.com/show_bug.cgi?id=1126751

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Feb 28 2014 Adrian Reber <adrian@lisas.de> - 1.2-1
- Update to 1.2
- Dropped all upstreamed patches

* Tue Feb 04 2014 Adrian Reber <adrian@lisas.de> - 1.1-4
- Create -devel subpackage

* Wed Dec 11 2013 Andrew Vagin <avagin@openvz.org> - 1.0-3
- Fix the epoch of crtools

* Tue Dec 10 2013 Andrew Vagin <avagin@openvz.org> - 1.0-2
- Rename crtools to criu #1034677

* Wed Nov 27 2013 Andrew Vagin <avagin@openvz.org> - 1.0-1
- Update to 1.0

* Thu Oct 24 2013 Andrew Vagin <avagin@openvz.org> - 0.8-1
- Update to 0.8

* Tue Sep 10 2013 Andrew Vagin <avagin@openvz.org> - 0.7-1
- Update to 0.7

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 24 2013 Andrew Vagin <avagin@openvz.org> - 0.6-3
- Delete all kind of -fstack-protector gcc options

* Wed Jul 24 2013 Andrew Vagin <avagin@openvz.org> - 0.6-3
- Added arm macro to ExclusiveArch

* Wed Jul 03 2013 Andrew Vagin <avagin@openvz.org> - 0.6-2
- fix building on ARM
- fix null pointer dereference

* Tue Jul 02 2013 Adrian Reber <adrian@lisas.de> - 0.6-1
- updated to 0.6
- upstream moved binaries to sbin
- using upstream's make install

* Tue May 14 2013 Adrian Reber <adrian@lisas.de> - 0.5-1
- updated to 0.5

* Fri Feb 22 2013 Adrian Reber <adrian@lisas.de> - 0.4-1
- updated to 0.4

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan 22 2013 Adrian Reber <adrian@lisas.de> - 0.3-3
- added ExclusiveArch blocker bug

* Fri Jan 18 2013 Adrian Reber <adrian@lisas.de> - 0.3-2
- improved Summary and Description

* Mon Jan 14 2013 Adrian Reber <adrian@lisas.de> - 0.3-1
- updated to 0.3
- fix building Documentation/

* Tue Aug 21 2012 Adrian Reber <adrian@lisas.de> - 0.2-2
- remove macros like %%{__mkdir_p} and %%{__install}
- add comment why it is only x86_64

* Tue Aug 21 2012 Adrian Reber <adrian@lisas.de> - 0.2-1
- initial release
