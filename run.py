
from src.app import config_app
from src import routes

app = config_app()
routes.init_app(app)

if __name__ == '__main__':
    app.run(debug = True)