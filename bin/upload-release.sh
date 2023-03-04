rm dist/*
set -e

bin/regen-docs.sh
# pandoc --from=markdown --to=rst --output=README README.md
python3 -m build
python3 -m twine check dist/*
python3 -m twine upload dist/*
echo new version at https://pypi.org/project/steamback