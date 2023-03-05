rm dist/*
set -e

bin/regen-docs.sh
# pandoc --from=markdown --to=rst --output=README README.md
python3 -m build
python3 -m twine check dist/*
# use API key per https://pypi.org/manage/account/token/ and ~/.pypirc
python3 -m twine upload --repository steamback dist/*
echo new version at https://pypi.org/project/steamback