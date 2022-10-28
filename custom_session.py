from sqlalchemy.orm import scoped_session


class M_scoped_session:
    Session = None
    def __init__(self, Session_factory):
        self.Session = scoped_session(Session_factory)

    def __enter__(self):
        return self.Session()

    def __exit__(self, exc_type, exc_value, tb):
        self.Session.remove()
        return True