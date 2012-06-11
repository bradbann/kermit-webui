VERSION		= $(shell git shortlog | grep -E '^[ ]+\w+' | wc -l)
NEWRELEASE	= $(shell echo $$(($(RELEASE) + 1)))

MESSAGESPOT=po/messages.pot


TOPDIR = $(shell pwd)
DATE="date +%Y%m%d"
PROGRAMNAME=kermit-webui
VERSION=$(shell grep "Version:" ./misc/specs/kermit-webui.spec)
RELEASE=`expr substr '${VERSION}' 10 5`
TMPDIR=/tmp
BUILDDIR=build
BRANCH=production

all: rpms


manpage:

messages:

bumprelease:	

#setversion: 

build: clean
	echo $(RELEASE)
	echo $(TOPDIR)
	echo "- Create Changelog file"
	git shortlog > changelog.txt
	mkdir -p ./dist
	git archive --format=tar --prefix=$(PROGRAMNAME)/ $(BRANCH) | gzip > ./dist/$(PROGRAMNAME)-$(RELEASE).tar.gz

clean:
	rm -rf dist/ 
	rm -rf rpm-build/
	rm -rf $(TMPDIR)/$(BUILDDIR)
	find . -name *.pyc -exec m -rf {} \;

clean_hard:

clean_harder:

clean_hardest: clean_rpms


install: build manpage

install_hard: clean_hard install

install_harder: clean_harder install

install_hardest: clean_harder clean_rpms rpms install_rpm restart

install_rpm:

restart:

recombuild: install_harder restart

clean_rpms:
	-rpm -e kermit-webui

sdist: messages

new-rpms: bumprelease rpms

pychecker:

pyflakes:

money: clean

async: install
	/sbin/service httpd restart

testit: clean

unittest:

rpms: build manpage sdist
	mkdir -p rpm-build
	cp dist/*.gz rpm-build/
	rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define '_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
	--define "_specdir %{_topdir}" \
	--define "_sourcedir  %{_topdir}" \
	--define "vendor Think" \
	-ba misc/specs/kermit-webui.spec
