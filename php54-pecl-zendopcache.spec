%global php_apiver  %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP API => //p') | tail -1)
%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}

# Build ZTS extension or only NTS
%global with_zts      1

%define basepkg   php54w
%define pecl_name zendopcache

Name:           %{basepkg}-pecl-zendopcache
Version:        7.0.2
Release:        1%{?dist}
Summary:        PECL package for Zend OPcache

License:        BSD
Group:          Development/Languages
URL:            http://pecl.php.net/package/zendopcache
Source0:        http://pecl.php.net/get/zendopcache-%{version}.tgz
Source1:        opcache.ini

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  automake %{basepkg}-devel %{basepkg}-pear >= 1:1.4.9-1.2

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Provides:       php-pecl(OPcache) = %{version}

%if 0%{?php_zend_api}
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
%else
Requires:       php-api = %{php_apiver}
%endif

%description
The Zend OPcache provides faster PHP execution through opcode caching and
optimization. It improves PHP performance by storing precompiled script
bytecode in the shared memory. This eliminates the stages of reading code from
the disk and compiling it on future access. In addition, it applies a few
bytecode optimization patterns that make code execution faster.


%prep
%setup -qc
[ -f package2.xml ] || mv package.xml package2.xml
mv package2.xml %{pecl_name}.xml

%if %{with_zts}
cp -r %{pecl_name}-%{version} %{pecl_name}-%{version}-zts
%endif


%build

pushd %{pecl_name}-%{version}
phpize
%configure --enable-opcache --with-php-config=%{_bindir}/php-config
CFLAGS="$RPM_OPT_FLAGS" make
popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts
phpize
%configure --enable-opcache --with-php-config=%{_bindir}/zts-php-config
CFLAGS="$RPM_OPT_FLAGS" make
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT

pushd %{pecl_name}-%{version}

make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install config file
install -d $RPM_BUILD_ROOT%{php_inidir}
echo "zend_extension=%{php_extdir}/opcache.so" > $RPM_BUILD_ROOT%{php_inidir}/opcache.ini
cat %{SOURCE1} >> $RPM_BUILD_ROOT%{php_inidir}/opcache.ini

popd

%if %{with_zts}
pushd %{pecl_name}-%{version}-zts

make install INSTALL_ROOT=$RPM_BUILD_ROOT

# install config file
install -d $RPM_BUILD_ROOT%{php_ztsinidir}
echo "zend_extension=%{php_ztsextdir}/opcache.so" > $RPM_BUILD_ROOT%{php_ztsinidir}/opcache.ini
cat %{SOURCE1} >> $RPM_BUILD_ROOT%{php_ztsinidir}/opcache.ini

popd
%endif


# Install XML package description
install -d $RPM_BUILD_ROOT%{pecl_xmldir}
install -pm 644 %{pecl_name}.xml $RPM_BUILD_ROOT%{pecl_xmldir}/%{pecl_name}.xml


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc %{pecl_name}-%{version}/{LICENSE,README}
%config(noreplace) %attr(644,root,root) %{php_inidir}/opcache.ini
%{php_extdir}/opcache.so
%{pecl_xmldir}/%{pecl_name}.xml

%if %{with_zts}
%config(noreplace) %attr(644,root,root) %{php_ztsinidir}/opcache.ini
%{php_ztsextdir}/opcache.so
%endif


%changelog
* Sat Jul 20 2013 Andy Thompson <andy@webtatic.com> 7.0.2-1
- Update to Opcache 7.0.2
- Add ZTS extension compilation

* Sat May 18 2013 Andy Thompson <andy@webtatic.com> 7.0.1-1
- create spec for OPcache 7.0.1