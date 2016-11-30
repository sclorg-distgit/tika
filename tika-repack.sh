#!/bin/sh

if [ $# -ne 1 ]  ; then
    echo "Usage: ./create-sources VERSION"
    exit 1
fi
VERSION=$1
rm -Rf tika-$VERSION-clean.tar.xz
#wget http://www.apache.org/dist/tika/tika-$VERSION-src.zip
wget https://archive.apache.org/dist/tika/tika-$VERSION-src.zip
unzip tika-$VERSION-src.zip

find tika-$VERSION -name "*.class" -print -delete
find tika-$VERSION -name "*.jar" -print -delete
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/testLinux-*-*
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/testFreeBSD-*
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/testSolaris-*
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/*.ibooks
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/*.numbers
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/*.pages
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/*.key
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/*.war
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/*.wma
rm -Rf tika-$VERSION/tika-parsers/src/test/resources/test-documents/*.wmv
find tika-$VERSION -name '*.7z' -print -delete
find tika-$VERSION -name '*.ar' -print -delete
find tika-$VERSION -name '*.cpio' -print -delete
find tika-$VERSION -name '*.ear' -print -delete
find tika-$VERSION -name '*.exe' -print -delete
find tika-$VERSION -name '*.mp*' -print -delete
find tika-$VERSION -name '*.mp3' -print -delete
find tika-$VERSION -name '*.tbz2' -print -delete
find tika-$VERSION -name '*.tgz' -print -delete
find tika-$VERSION -name '*.zip' -print  -delete
find tika-$VERSION -name '*.tar' -print  -delete
find tika-$VERSION -name '*.rar' -print  -delete
find tika-$VERSION -name '*.swf' -print  -delete

tar -cJf tika-$VERSION-clean.tar.xz tika-$VERSION
rm -rf tika-$VERSION
