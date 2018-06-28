clean:
	rm -f state.p *.pyc gschemas.compiled \
	rm -rf __pycache__ 

git-clean:
	rm -rf .git

schema-local:
	glib-compile-schemas --strict .
