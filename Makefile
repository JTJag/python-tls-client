.PHONY: update-libs build publish clean

update-libs:
	@echo Updating shared libraries...
	poetry run python scripts/update_shared_libraries.py

build: update-libs
	@echo Building package with Poetry...
	poetry build

publish: build
	@echo Publishing to PyPI
	poetry publish

clean:
	@echo Cleaning dist and egg-info...
	poetry run python -c "import shutil, glob, os; [shutil.rmtree(p, ignore_errors=True) for p in glob.glob('dist') + glob.glob('*.egg-info')]"