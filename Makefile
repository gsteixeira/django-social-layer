


default: test
	# build the package
	python -m build
	# check distribuition
	twine check dist/*

	
test:
	# test it
	cd example/app/ ; \
		python manage.py test social_layer infscroll .

lint:
	find ./ -name "*.py" -type f -exec sed -i 's/ \+$$//g' {} \;
	find ./ -name "*.html" -type f -exec sed -i 's/ \+$$//g' {} \;
	isort --profile black .
	black .
