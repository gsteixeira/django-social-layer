


default: test
	# build the package
	python -m build
	# check distribuition
	twine check dist/*

	
test:
	# test it
	cd example/app/ ; \
		python manage.py test social_layer infscroll .
