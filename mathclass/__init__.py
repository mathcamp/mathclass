from zope.sqlalchemy import ZopeTransactionExtension
from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

def db(request):
    """ Access a sqlite session object """
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        """ Close the session after the request """
        session.close()
    request.add_finished_callback(cleanup)

    return session

def main(global_config, **settings):
    """ This function returns a WSGI application.

    It is usually called by the PasteDeploy framework during
    ``paster serve``.
    """
    settings = dict(settings)
    print settings
    config = Configurator(settings=settings)

    engine = engine_from_config(settings, prefix='sqlalchemy.')
    # Create the schema if necessary
    from .models import Base
    Base.metadata.create_all(bind=engine)

    config.registry.dbmaker = sessionmaker(bind=engine,
                                           extension=ZopeTransactionExtension())
    config.add_request_method(db, reify=True)

    config.add_jinja2_search_path("mathclass:templates")
    config.add_static_view('static', 'static', cache_max_age=settings.get('pyramid.cache_max_age'))
    config.add_route('root', '/')
    config.add_route('upload', '/upload')
    config.add_route('talks', '/_fragment/')
    config.add_route('talk', r'/_fragment/talk/{id:\d+}')
    config.scan()
    return config.make_wsgi_app()
