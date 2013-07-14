Name:           TOPCOM
Version:        0.17.4
Release:        1%{?dist}
Summary:        Triangulations Of Point Configurations and Oriented Matroids

License:        GPLv2+
URL:            http://www.rambau.wm.uni-bayreuth.de/TOPCOM/
Source0:        http://www.rambau.wm.uni-bayreuth.de/Software/%{name}-%{version}.tar.gz
# Man pages, written by Jerry James using text from the sources.  Therefore,
# these man pages have the same copyright and license as the sources.
Source1:        %{name}-man.tar.xz
# A replacement Makefile.  See the %%build section for more information.
Source2:        %{name}-Makefile

BuildRequires:  cddlib-devel
BuildRequires:  gmp-devel
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%global topcom_major $(echo %{version} | cut -d. -f1)
%global topcom_minor $(echo %{version} | cut -d. -f2)

%description
TOPCOM is a package for computing Triangulations Of Point Configurations
and Oriented Matroids.  It was very much inspired by the maple program
PUNTOS, which was written by Jesus de Loera.  TOPCOM is entirely written
in C++, so there is a significant speed up compared to PUNTOS.

%package devel
Summary:        Header files needed to build with %{name}
Group:          Development/Libraries
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       cddlib-devel%{?_isa}
Requires:       gmp-devel%{?_isa}

%description devel
Header files needed to build applications that use the %{name} library.

%package libs
Summary:        Core %{name} functionality in a library
Group:          Development/Libraries

%description libs
Command line tools that expose %{name} library functionality.

%prep
%setup -q
%setup -q -T -D -a 1

# Fix character encoding
iconv -f iso8859-1 -t utf8 -o README.utf8 README
touch -r README README.utf8
mv -f README.utf8 README

# Mimic upstream's modification of gmpxx.h, using the system gmpxx.h
mkdir -p external/include
sed "s|// \(q\.canonicalize\)|\1|" %{_includedir}/gmpxx.h > \
  external/include/gmpxx.h

%build
# We cannot use upstream's build system.  It has the following problems.
# (1) It builds two static libraries, libTOPCOM.a and libCHECKREG.a, then
#     includes both libraries in each of the 38 binaries that it installs in
#     %%{_bindir}.
# (2) Each of libTOPCOM.a and libCHECKREG.a refers to symbols defined by the
#     other.
# (3) It builds static gmp and cddlib libraries, which are also linked into
#     all of the constructed binaries.  There is no way to make it use the
#     installed versions of those libraries instead.
# We could fix (3) with a little build system hackery.  We could fix (1) by
# building shared libraries, but that doesn't help with (2).  Instead, we pull
# in our own evilly constructed Makefile to build a single shared library
# containing all of the object files in both libTOPCOM.a and libCHECKREG.a,
# and link the binaries against that and the system gmp and cddlib libraries.
sed -e "s|@RPM_OPT_FLAGS@|${RPM_OPT_FLAGS}|" \
    -e "s|@bindir@|%{_bindir}|" \
    -e "s|@libdir@|%{_libdir}|" \
    -e "s|@mandir@|%{_mandir}|" \
    -e "s|@includedir@|%{_includedir}|" \
    -e "s|@version@|%{version}|" \
    -e "s|@major@|%{topcom_major}|" \
    -e "s|@minor@|%{topcom_minor}|" \
    -e "s|#version#|@version@|" \
    %{SOURCE2} > Makefile
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT

# Fix a too-generic name
mv $RPM_BUILD_ROOT%{_bindir}/bench $RPM_BUILD_ROOT%{_bindir}/%{name}_bench

# Get rid of the Makefiles in the examples dir before packaging
rm -f examples/Makefile*

%files
%doc examples
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/man7/*

%files devel
%{_includedir}/%{name}/
%{_libdir}/*.so

%files libs
%doc AUTHORS ChangeLog COPYING README
%{_libdir}/*.so.*
