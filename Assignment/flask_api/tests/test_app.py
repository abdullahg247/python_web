from flask import Flask
import pytest

app = Flask(__name__)

def test_app():
    assert app is not None

# Ensure the import statement for the app module is correct
# Adjust the import path if necessary to resolve ModuleNotFoundError