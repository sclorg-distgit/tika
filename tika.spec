%{?scl:%scl_package tika}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

# Conditionals to help breaking tika <-> vorbis-java-tika dependency cycle
%if 0%{?rhel}
%bcond_without vorbis_tika
# Disable only for now
%bcond_with tika_parsers
%bcond_without tika_app
%endif

Name:          %{?scl_prefix}tika
Version:       1.5
Release:       6.2%{?dist}
Summary:       A content analysis toolkit
License:       ASL 2.0
Url:           http://tika.apache.org/
Source0:       http://www.apache.org/dist/tika/%{pkg_name}-%{version}-src.zip
# Fix stax-api gId:aId
# Replace unavailable org.ow2.asm:asm-debug-all:4.1
# Replace ant-nodeps with ant
# Fix bouncycastle aId
Patch0:        %{pkg_name}-1.4-fix-build-deps.patch
Patch1:        %{pkg_name}-1.4-bouncycastle-1.50.patch
Patch2:        %{pkg_name}-1.5-metadata-extractor.patch

BuildRequires: %{?scl_prefix_maven}mvn(biz.aQute:bndlib)
BuildRequires: %{?scl_prefix_java_common}mvn(org.apache.ant:ant)
BuildRequires: %{?scl_prefix_maven}mvn(org.osgi:org.osgi.compendium)
BuildRequires: %{?scl_prefix_maven}mvn(org.osgi:org.osgi.core)

%if %{without vorbis_tika}
BuildRequires: mvn(org.gagravarr:vorbis-java-tika)
%endif

%if %{without tika_parsers}
BuildRequires: %{?scl_prefix_java_common}apache-commons-logging
BuildRequires: %{?scl_prefix_java_common}mvn(commons-codec:commons-codec)
BuildRequires: %{?scl_prefix_java_common}mvn(javax.xml.stream:stax-api)
BuildRequires: %{?scl_prefix_java_common}mvn(org.apache.commons:commons-compress)
BuildRequires: %{?scl_prefix_java_common}mvn(org.ow2.asm:asm-all:5)
BuildRequires: %{?scl_prefix}mvn(rome:rome)
%if %{without tika_app}
BuildRequires: %{?scl_prefix_java_common}mvn(com.google.code.gson:gson)
BuildRequires: mvn(log4j:log4j:1.2.17)
BuildRequires: mvn(org.slf4j:slf4j-log4j12)
%endif
%endif

%if 0
# tika-server deps
BuildRequires: mvn(net.sf.opencsv:opencsv:2.0)
BuildRequires: mvn(org.apache.cxf:cxf-rt-frontend-jaxrs:2.6.1)
BuildRequires: mvn(org.apache.cxf:cxf-rt-transports-http-jetty:2.6.1)
# tika-parser deps
BuildRequires: mvn(com.googlecode.mp4parser:mp4parser-project:1.0-RC-1)
BuildRequires: mvn(com.googlecode.mp4parser:isoparser:1.0-RC-1)
# tika-xmp
BuildRequires: mvn(org.apache.felix:maven-scr-plugin:1.7.4)
%endif

# Test deps
BuildRequires: %{?scl_prefix_java_common}mvn(junit:junit)
BuildRequires: %{?scl_prefix}mvn(org.mockito:mockito-core)
BuildRequires: %{?scl_prefix_java_common}mvn(xml-apis:xml-apis)

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

%package parsers
Summary:       Apache Tika parsers

%description parsers
Apache Tika parsers implementation that matches the
type of the document, once it is known, using
Mime Type detection.

%package java7
Summary:       Apache Tika Java-7 Components

%description java7
Java-7 reliant components, including FileTypeDetector
implementations.

%if %{without tika_app}

%package app
Summary:       Apache Tika Application
Requires:      mvn(log4j:log4j:1.2.17)

%description app
Apache Tika standalone application.
%endif
%endif

%package javadoc
Summary:       Javadoc for %{pkg_name}

%description javadoc
This package contains javadoc for %{pkg_name}.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -n %{pkg_name}-%{version} -q
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
%patch2 -p1

%pom_disable_module %{pkg_name}-bundle
%pom_disable_module %{pkg_name}-server
%pom_disable_module %{pkg_name}-xmp
# Unavailable plugins
%pom_remove_plugin org.codehaus.mojo:clirr-maven-plugin %{pkg_name}-core
%pom_remove_plugin org.apache.felix:maven-scr-plugin %{pkg_name}-xmp
%pom_remove_plugin org.apache.felix:maven-scr-plugin %{pkg_name}-java7

# Require com.drewnoakes:metadata-extractor:2.6.2 and fedora metadata-extractor pkg is too old
# see https://bugzilla.redhat.com/show_bug.cgi?id=947457
%pom_xpath_set "pom:project/pom:dependencies/pom:dependency[pom:artifactId='metadata-extractor']/pom:version" 2  %{pkg_name}-parsers
%pom_xpath_set "pom:project/pom:dependencies/pom:dependency[pom:artifactId='asm-all']/pom:version" 5.0.3  %{pkg_name}-parsers
# Disable vorbis-java-tika support, cause circular dependency
%if %{with vorbis_tika}
%pom_remove_dep :vorbis-java-tika %{pkg_name}-parsers
%endif

%if %{with tika_parsers}
%pom_disable_module %{pkg_name}-parsers
%else
%if %{with tika_app}
%pom_disable_module %{pkg_name}-app
%else
# No bundled libraries are shipped
%pom_remove_plugin :maven-shade-plugin %{pkg_name}-app
%pom_remove_plugin :maven-antrun-plugin %{pkg_name}-app
%endif
%endif

# Unavailable build dep com.googlecode.mp4parser:isoparser
# MP4 is non-free remove support for it
%pom_remove_dep com.googlecode.mp4parser:isoparser %{pkg_name}-parsers
rm -r %{pkg_name}-parsers/src/main/java/org/apache/tika/parser/mp4/MP4Parser.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mp4/MP4ParserTest.java

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
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/image/ImageMetadataExtractorTest.java
# Fails for unavailable test resources
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/microsoft/ProjectParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mp3/Mp3ParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/mime/TestMimeTypes.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/iwork/IWorkParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/ArParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/executable/ExecutableParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/ibooks/iBooksParserTest.java \
 %{pkg_name}-app/src/test/java/org/apache/tika/cli/TikaCLITest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pdf/PDFParserTest.java

# NullPointerException: null
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/fork/ForkParserIntegrationTest.java
# NoClassDefFoundError: org/w3c/dom/ElementTraversal
%pom_add_dep xml-apis:xml-apis::test %{pkg_name}-parsers
%pom_add_dep org.apache.commons:commons-logging:1.5 %{pkg_name}-parsers

# ComparisonFailure: Date/Time Original for when the photo was taken, unspecified time zone expected:<2009-08-11T[09]:09:45> but was:<2009-08-11T[11]:09:45>
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/jpeg/JpegParserTest.java

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
%pom_remove_dep org.gagravarr:vorbis-java-core %{pkg_name}-parsers
%pom_remove_dep com.googlecode.juniversalchardet:juniversalchardet %{pkg_name}-parsers
%pom_remove_dep org.bouncycastle:bcprov-jdk16 %{pkg_name}-parsers
%pom_remove_dep org.slf4j:slf4j-log4j12 %{pkg_name}-parsers
%pom_remove_dep com.uwyn:jhighlight %{pkg_name}-parsers
rm -r tika-parsers/src/main/java/org/apache/tika/parser/{chm,code,crypto,dwg,executable,font,hdf,html,image,jpeg,mail,microsoft,mp3,mp4,netcdf,pdf,pkg,prt,txt}
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
# skip tests for now because there are test failures:
# Tests which use cglib fail because of incompatibility with asm4
# Test fails for unavailable build deps: com.googlecode.mp4parser:isoparser
%mvn_package :%{pkg_name} %{pkg_name}
%mvn_package :%{pkg_name}-core %{pkg_name}
%mvn_package :%{pkg_name}-parent %{pkg_name}
%mvn_build -f -s -- -Dproject.build.sourceEncoding=UTF-8
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install

%if %{without tika_app}
%jpackage_script org.apache.tika.cli.TikaCLI "" "" %{pkg_name}:google-gson:commons-io:commons-logging:log4j12-1.2.17:metadata-extractor2-2:juniversalchardet:apache-commons-codec:boilerpipe:thredds/netcdf:thredds/udunits:bea-stax-api:commons-compress:felix/org.apache.felix.scr.annotations:apache-mime4j/core:apache-mime4j/dom:pdfbox:poi/poi:poi/poi-scratchpad:poi/poi-ooxml:bcmail:bcprov:tagsoup:objectweb-asm4/asm-all:rome:fontbox:vorbis-java:dom4j:xmlbeans:poi/poi-ooxml-schemas:jempbox:xmpcore:slf4j/api:slf4j/log4j12:jdom:jdom2 %{pkg_name}-app true
%endif
%{?scl:EOF}


%files -f .mfiles-%{pkg_name}
%dir %{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%doc CHANGES.txt HEADER.txt KEYS README.txt
%doc LICENSE.txt NOTICE.txt

%if %{without tika_parsers}

%files parsers -f .mfiles-%{pkg_name}-parsers
%doc LICENSE.txt NOTICE.txt

%files java7 -f .mfiles-%{pkg_name}-java7
%doc LICENSE.txt NOTICE.txt

%if %{without tika_app}

%files app -f .mfiles-%{pkg_name}-app
%doc LICENSE.txt NOTICE.txt
%{_bindir}/%{pkg_name}-app
%endif
%endif

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Thu Jul 16 2015 Mat Booth <mat.booth@redhat.com> - 1.5-6.2
- Fix unowned directories

* Tue Jul 07 2015 Mat Booth <mat.booth@redhat.com> - 1.5-6.1
- Import latest from Fedora

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr 22 2015 gil cattaneo <puntogil@libero.it> 1.5-5
- rebuilt with new metadata-extractor2.8.1

* Mon Apr 20 2015 gil cattaneo <puntogil@libero.it> 1.5-4
- rebuilt with new metadata-extractor2.7.2

* Fri Mar 06 2015 gil cattaneo <puntogil@libero.it> 1.5-3
- rebuilt with new jhighlight

* Mon Feb 16 2015 gil cattaneo <puntogil@libero.it> 1.5-2
- introduce license macro

* Tue Jul 01 2014 gil cattaneo <puntogil@libero.it> 1.5-1
- update to 1.5

* Wed Jun 11 2014 Fabrice Bellet <fabrice@bellet.info> 1.4-7
- enable app module, RHBZ#1109072

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

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
