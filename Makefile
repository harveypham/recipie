build: recipie/*.py
	python -m build

release: dist/*
	python -m twine upload -r pypi dist/*

test:
	cd tests && python test.py