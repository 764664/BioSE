from src import app
from src.helpers.update import update
import os

if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    update()
app.run(debug=True, host='0.0.0.0', threaded=True)

