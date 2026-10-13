from . import auth, exams, papers, questions, scores, stats, users

_BLUEPRINTS = (auth, users, questions, papers, exams, stats, scores)


def register_blueprints(app):
    for module in _BLUEPRINTS:
        app.register_blueprint(module.bp, url_prefix="/api")
