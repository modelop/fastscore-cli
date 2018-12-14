BUILD_VOL=\
	if [ -f /.dockerenv ]; then\
		SRC=`docker inspect --format='{{range .Mounts}}{{if (eq .Destination "/drone")}}{{.Source}}{{end}}{{end}}' $$HOSTNAME`;\
		VOL=$${SRC}$${DRONE_WORKSPACE\#/drone};\
	else \
		VOL=$(PWD);\
	fi &&

build:
	docker build -f Dockerfile.build -t build/cli .
	$(BUILD_VOL) docker run --rm -v $$VOL:/cli build/cli make dist

dist:
	cd sdk &&\
		rm -rf build && python2 setup.py bdist_wheel &&\
		rm -rf build && python3 setup.py bdist_wheel
	rm -rf build && python2 setup.py bdist_wheel
	rm -rf build && python3 setup.py bdist_wheel

test:
## TODO (for SDK):
##   python2 setup.py test
##   python3 setup.py test
	docker build -f Dockerfile.test -t test/cli .

.PHONY: build dist test
