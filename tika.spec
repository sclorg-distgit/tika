# Conditionals to help breaking tika <-> vorbis-java-tika dependency cycle
%if 0%{?fedora}
%bcond_with vorbis_tika
%bcond_with tika_parsers
%endif

%{?scl:%scl_package tika}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

Name:          %{?scl_prefix}tika
Version:       1.4
Release:       6%{?dist}
Summary:       A content analysis toolkit
License:       ASL 2.0
Url:           http://tika.apache.org/
# http://www.apache.org/dist/tika/%{pkg_name}-%{version}-src.zip
# delete tika-app, tika-dotnet, tika-server tika-xmp
# Remove all parsers except for epub and xml
Source0:       %{pkg_name}-%{version}-minimal.zip

# Fix stax-api gId:aId
# Replace unavailable org.ow2.asm:asm-debug-all:4.1
# Replace ant-nodeps with ant
# Fix bouncycastle aId
Patch0:        %{pkg_name}-1.4-fix-build-deps.patch
Patch1:        %{pkg_name}-1.4-add-apache-commons-logging_dep.patch

BuildRequires: %{?scl_prefix_maven}aqute-bndlib
BuildRequires: %{?scl_prefix_java_common}ant
BuildRequires: %{?scl_prefix_maven}felix-osgi-compendium
BuildRequires: %{?scl_prefix_maven}felix-osgi-core

%if %{without tika_parsers}
BuildRequires: %{?scl_prefix_java_common}apache-commons-logging
%endif

# Test deps
BuildRequires: %{?scl_prefix_java_common}junit
BuildRequires: %{?scl_prefix}mockito
BuildRequires: %{?scl_prefix_java_common}slf4j

BuildRequires: %{?scl_prefix_java_common}maven-local
BuildRequires: %{?scl_prefix_maven}maven-failsafe-plugin
BuildRequires: %{?scl_prefix_maven}maven-plugin-bundle
BuildRequires: %{?scl_prefix_maven}maven-remote-resources-plugin
BuildRequires: %{?scl_prefix_maven}maven-site-plugin

BuildArch:     noarch

%description
The Apache Tika toolkit detects and extracts meta-data and
structured text content from various documents using existing
parser libraries.

%if %{without tika_parsers}
%package parsers-epub
Summary:       Apache Tika parser for epub

%description parsers-epub
Apache Tika parsers implementation for the epub
format

#%package xmp
#Summary:       Apache Tika XMP

#%description xmp
#Converts Tika metadata to XMP.
%endif

%package javadoc
Summary:       Javadoc for %{pkg_name}

%description javadoc
This package contains javadoc for %{pkg_name}.

%prep
%setup -q -n tika-%{version}-minimal
# Cleanup
find . -name '*.jar' -delete
find . -name '*.class' -delete
# Remove unwanted test resources
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/testLinux-*-*
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/testFreeBSD-*
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/testSolaris-*
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/*.ibooks
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/*.numbers
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/*.pages
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/*.key
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/*.war
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/*.wma
rm -r %{pkg_name}-parsers/src/test/resources/test-documents/*.wmv
find . -name '*.7z' -delete
find . -name '*.ar' -delete
find . -name '*.cpio' -delete
find . -name '*.ear' -delete
find . -name '*.exe' -delete
find . -name '*.mp*' -delete
find . -name '*.tbz2' -delete
find . -name '*.tgz' -delete
find . -name '*.zip' -delete
%patch0 -p1
%patch1 -p1

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%pom_disable_module %{pkg_name}-app
%pom_disable_module %{pkg_name}-bundle
%pom_disable_module %{pkg_name}-server
# Unavailable plugins
%pom_remove_plugin org.codehaus.mojo:clirr-maven-plugin %{pkg_name}-core
#%pom_remove_plugin org.apache.felix:maven-scr-plugin %{pkg_name}-xmp

# Require com.drewnoakes:metadata-extractor:2.6.2 and fedora metadata-extractor pkg is too old
# see https://bugzilla.redhat.com/show_bug.cgi?id=947457
%pom_xpath_set "pom:project/pom:dependencies/pom:dependency[pom:artifactId='metadata-extractor']/pom:version" 2  %{pkg_name}-parsers
# Disable vorbis-java-tika support, cause circular dependency
%if %{with vorbis_tika}
%pom_remove_dep :vorbis-java-tika %{pkg_name}-parsers
%endif

%pom_disable_module %{pkg_name}-xmp

%if %{with tika_parsers}
%pom_disable_module %{pkg_name}-parsers
%endif

# Unavailable build dep com.googlecode.mp4parser:isoparser
# MP4 is non-free remove support for it
%pom_remove_dep com.googlecode.mp4parser:isoparser %{pkg_name}-parsers

# This test require network
rm %{pkg_name}-core/src/test/java/org/apache/tika/mime/MimeDetectionTest.java
# These test fails for unavailable deps: com.googlecode.mp4parser:isoparser and org.gagravarr:vorbis-java-tika
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mail/RFC822ParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mbox/MboxParserTest.java
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/detect/TestContainerAwareDetector.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/AutoDetectParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/asm/ClassParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/Bzip2ParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/GzipParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/TarParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/ZipParserTest.java
#rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/image/ImageMetadataExtractorTest.java
# Fails for unavailable test resources
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/microsoft/ProjectParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mp3/Mp3ParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/mime/TestMimeTypes.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/iwork/IWorkParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/ArParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/executable/ExecutableParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/ibooks/iBooksParserTest.java

#Remove deps required by parsers other than epub
%pom_remove_dep org.apache.felix:org.apache.felix.scr.annotations %{pkg_name}-parsers
%pom_remove_dep edu.ucar:netcdf %{pkg_name}-parsers
%pom_remove_dep org.apache.james:apache-mime4j-core %{pkg_name}-parsers
%pom_remove_dep org.apache.james:apache-mime4j-dom %{pkg_name}-parsers
%pom_remove_dep org.apache.pdfbox:pdfbox %{pkg_name}-parsers
%pom_remove_dep org.bouncycastle:bcmail-jdk16 %{pkg_name}-parsers
%pom_remove_dep org.apache.poi:poi %{pkg_name}-parsers
%pom_remove_dep org.apache.poi:poi-scratchpad %{pkg_name}-parsers
%pom_remove_dep org.apache.poi:poi-ooxml %{pkg_name}-parsers
%pom_remove_dep org.ccil.cowan.tagsoup:tagsoup %{pkg_name}-parsers
%pom_remove_dep com.drewnoakes:metadata-extractor %{pkg_name}-parsers
%pom_remove_dep de.l3s.boilerpipe:boilerpipe %{pkg_name}-parsers
%pom_remove_dep rome:rome %{pkg_name}-parsers
%pom_remove_dep org.gagravarr:vorbis-java-core %{pkg_name}-parsers
%pom_remove_dep org.gagravarr:vorbis-java-tika %{pkg_name}-parsers
%pom_remove_dep com.googlecode.juniversalchardet:juniversalchardet %{pkg_name}-parsers
%pom_remove_dep org.bouncycastle:bcprov-jdk16 %{pkg_name}-parsers
%pom_remove_dep org.ow2.asm:asm-all %{pkg_name}-parsers
%pom_remove_dep org.slf4j:slf4j-log4j12 %{pkg_name}-parsers
%{?scl:EOF}

%build
# skip tests for now because there are test failures:
# Tests which use cglib fail because of incompatibility with asm4
# Test fails for unavailable build deps: com.googlecode.mp4parser:isoparser
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_package :%{pkg_name} %{pkg_name}
%mvn_package :%{pkg_name}-core %{pkg_name}
%mvn_package :%{pkg_name}-parent %{pkg_name}
%mvn_build -f -s -- -Dproject.build.sourceEncoding=UTF-8
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install
%{?scl:EOF}

%files -f .mfiles-%{pkg_name}
%dir %{_javadir}/%{pkg_name}
%doc CHANGES.txt HEADER.txt KEYS LICENSE.txt NOTICE.txt README.txt

%if %{without tika_parsers}
%files parsers-epub -f .mfiles-%{pkg_name}-parsers
%doc LICENSE.txt NOTICE.txt

#%files xmp -f .mfiles-%{pkg_name}-xmp
#%doc LICENSE.txt NOTICE.txt
%endif

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Mon May 11 2015 Mat Booth <mat.booth@redhat.com> - 1.4-6
- Resolves: rhbz#1219013 - Fails to build from source

* Thu May 29 2014 Sami Wagiaalla <swagiaal@redhat.com> - 1.4-5
- Scl-ize and build for DTS 3.0.
- Import package from rawhide.

* Fri Mar 07 2014 Michal Srb <msrb@redhat.com> - 1.4-5
- Port to bouncycastle 1.50

* Tue Nov 19 2013 gil cattaneo <puntogil@libero.it> 1.4-4
- enable vorbis-java-tika support

* Wed Oct 23 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.4-3
- Rebuild to regenerate broken POMs
- Related: rhbz#1021484

* Mon Oct 21 2013 gil cattaneo <puntogil@libero.it> 1.4-2
- enable parsers and xpm modules

* Thu Aug 29 2013 gil cattaneo <puntogil@libero.it> 1.4-1
- update to 1.4

* Tue Oct 23 2012 gil cattaneo <puntogil@libero.it> 1.2-1
- initial rpm
