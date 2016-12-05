from src import app
from src.helpers.update import update

update()
app.run(debug=True, host='0.0.0.0', threaded=True)

