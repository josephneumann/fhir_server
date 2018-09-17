# -*- coding: utf-8 -*-
"""Create an application instance."""
from app.app import create_app, CustomSessionInterface

app = create_app()
app.session_interface = CustomSessionInterface()  # Disable session cookie for API requests

# Enable old style app.run() method for Flask to allow pass-through of errors to Pycharm debugger
if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=True, passthrough_errors=True, threaded=False)
