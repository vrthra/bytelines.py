bytes:
	python3 -m compileall .
	cp __pycache__/sample.cpython-36.pyc .

reset:
	cp sample.cpython-36.pyc __pycache__/

hack:
	python3 bytes.py __pycache__/sample.cpython-36.pyc

run:
	python3 tracesample.py

clean:
	rm -rf __pycache__/
