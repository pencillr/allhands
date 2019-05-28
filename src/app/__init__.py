from flask import Flask

app = Flask(__name__)

# This bottom import is a workaround to circular imports,
# a common problem with Flask applications.
# Routes module needs to import the app variable defined in this script,
# so putting one of the reciprocal imports at the bottom avoids the error
# that results from the mutual references between these two files.

from app import routes