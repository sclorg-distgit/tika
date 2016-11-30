%{?scl:%scl_package tika}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

# Conditionals to help breaking tika <-> vorbis-java-tika dependency cycle
%bcond_without vorbis_tika
# Disable only for now
%bcond_with tika_parsers
%bcond_without tika_app

Name:          %{?scl_prefix}tika
Version:       1.11
Release:       2.%{baserelease}%{?dist}
Summary:       A content analysis toolkit
License:       ASL 2.0
Url:           http://tika.apache.org/
# sh tika-repack.sh <VERSION>
Source0:       %{pkg_name}-%{version}-clean.tar.xz
Source1:       tika-repack.sh

BuildRequires: %{?scl_prefix_maven}maven-local
BuildRequires: %{?scl_prefix_maven}mvn(biz.aQute:bndlib)
BuildRequires: %{?scl_prefix_java_common}mvn(com.google.code.gson:gson)
BuildRequires: %{?scl_prefix_java_common}mvn(junit:junit)
BuildRequires: %{?scl_prefix_java_common}mvn(org.apache.ant:ant)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-failsafe-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-remote-resources-plugin)
BuildRequires: %{?scl_prefix}mvn(org.mockito:mockito-core)
BuildRequires: %{?scl_prefix_maven}mvn(org.osgi:org.osgi.compendium)
BuildRequires: %{?scl_prefix_maven}mvn(org.osgi:org.osgi.core)
BuildRequires: %{?scl_prefix_java_common}mvn(xml-apis:xml-apis)

%if %{without vorbis_tika}
BuildRequires: mvn(org.gagravarr:vorbis-java-tika)
%endif

%if %{without tika_parsers}
BuildRequires: %{?scl_prefix}mvn(com.google.guava:guava)
BuildRequires: %{?scl_prefix_java_common}mvn(commons-cli:commons-cli)
BuildRequires: %{?scl_prefix_java_common}mvn(commons-codec:commons-codec)
BuildRequires: %{?scl_prefix_java_common}mvn(commons-io:commons-io)
%if %{without tika_app}
BuildRequires: mvn(log4j:log4j:1.2.17)
%endif
BuildRequires: %{?scl_prefix_java_common}mvn(org.apache.commons:commons-compress)
BuildRequires: %{?scl_prefix}mvn(rome:rome)
BuildRequires: %{?scl_prefix_java_common}mvn(org.tukaani:xz)
%endif

%if 0
# tika-parsers
BuildRequires: mvn(org.apache.cxf:cxf-rt-rs-client:3.0.3)
# tika-server deps
BuildRequires: %{?scl_prefix_java_common}mvn(commons-lang:commons-lang)
BuildRequires: %{?scl_prefix_java_common}mvn(javax.mail:mail)
BuildRequires: mvn(net.sf.opencsv:opencsv:2.0)
BuildRequires: mvn(org.apache.cxf:cxf-rt-frontend-jaxrs:3.0.3)
BuildRequires: mvn(org.apache.cxf:cxf-rt-transports-http-jetty:3.0.3)
BuildRequires: mvn(org.apache.cxf:cxf-rt-rs-client:3.0.3)
BuildRequires: mvn(org.apache.cxf:cxf-rt-rs-security-cors:3.0.3)
BuildRequires: mvn(org.apache.cxf:cxf-rt-rs-service-description:3.0.3)
BuildRequires: mvn(org.slf4j:slf4j-jcl)
# tika-translate
# https://gil.fedorapeople.org/microsoft-translator-java-api-0.6.2-1.fc19.src.rpm
BuildRequires: mvn(com.memetix:microsoft-translator-java-api)
BuildRequires: mvn(org.apache.cxf:cxf-rt-frontend-jaxrs:2.7.8)
BuildRequires: %{?scl_prefix}mvn(com.fasterxml.jackson.jaxrs:jackson-jaxrs-json-provider)
%endif

BuildArch:     noarch

%description
The Apache Tika toolkit detects and extracts meta-data and
structured text content from various documents using existing
parser libraries.

%if %{without tika_parsers}

%package parsers
Summary:       Apache Tika Parsers

%description parsers
Apache Tika Parsers implementation that matches the
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

%package serialization
Summary:       Apache Tika Serialization

%description serialization
Apache Tika Serialization integrated the
GSON library to serialize/deserialize
Metadata objects.

%package javadoc
Summary:       Javadoc for %{pkg_name}

%description javadoc
This package contains javadoc for %{pkg_name}.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -n %{pkg_name}-%{version} -q

%pom_disable_module %{pkg_name}-bundle
%pom_disable_module %{pkg_name}-example
%pom_disable_module %{pkg_name}-server
%pom_disable_module %{pkg_name}-translate
%pom_disable_module %{pkg_name}-batch
%pom_disable_module %{pkg_name}-xmp

# Unavailable plugins
%pom_remove_plugin org.codehaus.mojo:clirr-maven-plugin %{pkg_name}-core
%pom_remove_plugin org.apache.felix:maven-scr-plugin %{pkg_name}-xmp
%pom_remove_plugin org.apache.felix:maven-scr-plugin %{pkg_name}-java7
%pom_remove_plugin -r de.thetaphi:forbiddenapis %{pkg_name}-parent
%pom_remove_plugin :maven-shade-plugin %{pkg_name}-parent

%pom_change_dep :ant-nodeps :ant

# Require com.drewnoakes:metadata-extractor:2.6.2 and fedora metadata-extractor pkg is too old
# see https://bugzilla.redhat.com/show_bug.cgi?id=947457
%pom_xpath_set "pom:dependency[pom:artifactId='metadata-extractor']/pom:version" 2  %{pkg_name}-parsers
# Disable vorbis-java-tika support, cause circular dependency
%if %{with vorbis_tika}
%pom_remove_dep :vorbis-java-tika %{pkg_name}-parsers
%endif

%if %{with tika_parsers}
%pom_disable_module %{pkg_name}-parsers
%pom_disable_module %{pkg_name}-xmp
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
rm -rf %{pkg_name}-parsers/src/main/java/org/apache/tika/parser/mp4/MP4Parser.java \
 %{pkg_name}-parsers/src/main/java/org/apache/tika/parser/mp4/DirectFileReadDataSource.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mp4/MP4ParserTest.java
# NON FREE under UnRar License
%pom_remove_dep com.github.junrar:junrar %{pkg_name}-parsers
rm %{pkg_name}-parsers/src/main/java/org/apache/tika/parser/pkg/RarParser.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/RarParserTest.java
# sis & geoapi use NON FREE deps: javax.measure:jsr-275
%pom_remove_dep org.apache.sis.core:sis-utility %{pkg_name}-parsers
%pom_remove_dep org.apache.sis.storage:sis-netcdf %{pkg_name}-parsers
%pom_remove_dep org.apache.sis.core:sis-metadata %{pkg_name}-parsers
#  https://github.com/opengeospatial/geoapi/issues/8
%pom_remove_dep org.opengis:geoapi %{pkg_name}-parsers
rm -r %{pkg_name}-parsers/src/main/java/org/apache/tika/parser/geoinfo \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/geoinfo
%pom_remove_dep org.apache.ctakes:ctakes-core %{pkg_name}-parsers
rm -r %{pkg_name}-parsers/src/main/java/org/apache/tika/parser/ctakes

# Remove NON FREE json.org support
%pom_remove_dep org.json:json %{pkg_name}-parsers
rm -r %{pkg_name}-parsers/src/main/java/org/apache/tika/parser/journal \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/journal

# TODO org.apache.cxf:cxf-rt-rs-client:3.0.3 https://bugzilla.redhat.com/show_bug.cgi?id=1276555
%pom_remove_dep org.apache.cxf:cxf-rt-rs-client %{pkg_name}-parsers

# This test require network
rm %{pkg_name}-core/src/test/java/org/apache/tika/mime/MimeDetectionTest.java \
 tika-core/src/test/java/org/apache/tika/detect/MimeDetectionWithNNTest.java
# These test fails for unavailable deps: com.googlecode.mp4parser:isoparser and org.gagravarr:vorbis-java-tika
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mail/RFC822ParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/mbox/MboxParserTest.java
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/detect/TestContainerAwareDetector.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/AutoDetectParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/asm/ClassParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/Bzip2ParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/GzipParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/TarParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/ZipParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/ZlibParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/Seven7ParserTest.java \
 %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/pkg/CompressParserTest.java
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

# ComparisonFailure: Date/Time Original for when the photo was taken, unspecified time zone expected:<2009-08-11T[09]:09:45> but was:<2009-08-11T[11]:09:45>
rm -r %{pkg_name}-parsers/src/test/java/org/apache/tika/parser/jpeg/JpegParserTest.java
# Fail on ARM builder TestTimedOutException: test timed out after 30000 milliseconds
rm -r %{pkg_name}-batch/src/test/java/org/apache/tika/batch/fs/BatchDriverTest.java

%mvn_package :%{pkg_name} %{pkg_name}
%mvn_package :%{pkg_name}-core %{pkg_name}
%mvn_package :%{pkg_name}-parent %{pkg_name}

#Remove deps required by parsers other than epub
%pom_add_dep org.apache.commons:commons-logging %{pkg_name}-parsers
%pom_remove_dep com.healthmarketscience.jackcess:jackcess %{pkg_name}-parsers
%pom_remove_dep com.healthmarketscience.jackcess:jackcess-encrypt %{pkg_name}-parsers
%pom_remove_dep org.apache.felix:org.apache.felix.scr.annotations %{pkg_name}-parsers
%pom_remove_dep net.sourceforge.jmatio:jmatio %{pkg_name}-parsers
%pom_remove_dep org.apache.james:apache-mime4j-core %{pkg_name}-parsers
%pom_remove_dep org.apache.james:apache-mime4j-dom %{pkg_name}-parsers
%pom_remove_dep org.apache.pdfbox:pdfbox %{pkg_name}-parsers
%pom_remove_dep org.bouncycastle:bcmail-jdk15on %{pkg_name}-parsers
%pom_remove_dep org.bouncycastle:bcprov-jdk15on %{pkg_name}-parsers
%pom_remove_dep org.apache.poi:poi %{pkg_name}-parsers
%pom_remove_dep org.apache.poi:poi-scratchpad %{pkg_name}-parsers
%pom_remove_dep org.apache.poi:poi-ooxml %{pkg_name}-parsers
%pom_remove_dep org.ccil.cowan.tagsoup:tagsoup %{pkg_name}-parsers
%pom_remove_dep org.ow2.asm:asm %{pkg_name}-parsers
%pom_remove_dep com.drewnoakes:metadata-extractor %{pkg_name}-parsers
%pom_remove_dep de.l3s.boilerpipe:boilerpipe %{pkg_name}-parsers
%pom_remove_dep org.gagravarr:vorbis-java-core %{pkg_name}-parsers
%pom_remove_dep com.googlecode.juniversalchardet:juniversalchardet %{pkg_name}-parsers
%pom_remove_dep org.slf4j:slf4j-log4j12 %{pkg_name}-parsers
%pom_remove_dep org.codelibs:jhighlight %{pkg_name}-parsers
%pom_remove_dep com.pff:java-libpst %{pkg_name}-parsers
%pom_remove_dep org.xerial:sqlite-jdbc %{pkg_name}-parsers
%pom_remove_dep org.apache.opennlp:opennlp-tools %{pkg_name}-parsers
%pom_remove_dep org.apache.commons:commons-exec %{pkg_name}-parsers
%pom_remove_dep com.googlecode.json-simple:json-simple %{pkg_name}-parsers
%pom_remove_dep edu.ucar:netcdf4 %{pkg_name}-parsers
%pom_remove_dep edu.ucar:grib %{pkg_name}-parsers
%pom_remove_dep edu.ucar:cdm %{pkg_name}-parsers
%pom_remove_dep edu.ucar:httpservices %{pkg_name}-parsers
%pom_remove_dep org.apache.commons:commons-csv %{pkg_name}-parsers
rm -r tika-parsers/src/main/java/org/apache/tika/parser/{asm,chm,code,crypto,dif,dwg,executable,font,geo,grib,hdf,html,image,isatab,jdbc,jpeg,mail,mat,mbox,microsoft,mp3,mp4,netcdf,ocr,odf,opendocument,pdf,pkg,prt,rtf,txt}
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x

# skip tests for now because there are test failures:
# Tests which use cglib fail because of incompatibility with asm>=4
# Test fails for unavailable build deps: com.googlecode.mp4parser:isoparser
# On ARM builder only
# [ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:2.19:test (default-test)
# on project tika-batch: Execution default-test of goal org.apache.maven.plugins:maven-surefire-plugin:2.19:test
# failed: The forked VM terminated without properly saying goodbye. VM crash or System.exit called?
# [ERROR] Command was /bin/sh -c cd /builddir/build/BUILD/tika-1.11/tika-batch &&
# /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.65-5.b17.fc24.arm/jre/bin/java -Xmx2048m -jar
# /builddir/build/BUILD/tika-1.11/tika-batch/target/surefire/surefirebooter7260304071560324729.jar
# /builddir/build/BUILD/tika-1.11/tika-batch/target/surefire/surefire575868159465048587tmp
# /builddir/build/BUILD/tika-1.11/tika-batch/target/surefire/surefire_31877375323011518356tmp
# [ERROR] -> [Help 1]
%mvn_build -sf -- -Dproject.build.sourceEncoding=UTF-8
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install

%if %{without tika_app}
%jpackage_script org.apache.tika.cli.TikaCLI "" "" %{pkg_name}:opennlp:jwnl:google-gson:commons-io:commons-logging:log4j12-1.2.17:metadata-extractor2-2:juniversalchardet:apache-commons-codec:boilerpipe:thredds:bea-stax-api:commons-compress:felix/org.apache.felix.scr.annotations:apache-mime4j/core:apache-mime4j/dom:pdfbox:poi/poi:poi/poi-scratchpad:poi/poi-ooxml:bcmail:bcprov:tagsoup:objectweb-asm/asm-all:rome:fontbox:vorbis-java:dom4j:xmlbeans:poi/poi-ooxml-schemas:jempbox:xmpcore:slf4j/api:slf4j/log4j12:jdom:jdom2 %{pkg_name}-app true
%endif
%{?scl:EOF}


%files -f .mfiles-%{pkg_name}
%doc CHANGES.txt HEADER.txt KEYS README.md
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

%files serialization -f .mfiles-%{pkg_name}-serialization
%doc LICENSE.txt NOTICE.txt

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%changelog
* Thu Jul 28 2016 Mat Booth <mat.booth@redhat.com> - 1.11-2.2
- Disable batch and xmp modules
- Disable parsers that we cannot build and do not need

* Thu Jul 28 2016 Mat Booth <mat.booth@redhat.com> - 1.11-2.1
- Auto SCL-ise package for rh-eclipse46 collection

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Oct 30 2015 gil cattaneo <puntogil@libero.it> 1.11-1
- update to 1.11

* Tue Oct 06 2015 gil cattaneo <puntogil@libero.it> 1.9-2
- add opennlp support

* Wed Sep 02 2015 gil cattaneo <puntogil@libero.it> 1.9-1
- update to 1.9

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
