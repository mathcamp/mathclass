from zope.sqlalchemy import ZopeTransactionExtension
import pyramid.security
from pyramid.traversal import DefaultRootFactory
from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
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

class GoogleAuthPolicy(object):
    def __init__(self, settings):
        self._settings = settings

    def authenticated_userid(self, request):
        """ Return the authenticated userid or ``None`` if no
        authenticated userid can be found. This method of the policy
        should ensure that a record exists in whatever persistent store is
        used related to the user (the user should not have been deleted);
        if a record associated with the current id does not exist in a
        persistent store, it should return ``None``."""
        return request.session.get('username')

    def unauthenticated_userid(self, request):
        """ Return the *unauthenticated* userid.  This method performs the
        same duty as ``authenticated_userid`` but is permitted to return the
        userid based only on data present in the request; it needn't (and
        shouldn't) check any persistent store to ensure that the user record
        related to the request userid exists."""
        return request.session.get('username')

    def effective_principals(self, request):
        """ Return a sequence representing the effective principals
        including the userid and any groups belonged to by the current
        user, including 'system' groups such as
        ``pyramid.security.Everyone`` and
        ``pyramid.security.Authenticated``. """
        perms = [pyramid.security.Everyone]
        username = request.session.get('username')
        if username:
            perms.append(pyramid.security.Authenticated)
            if username in self._settings.get('auth.admins', []):
                perms.append('admin')
        return perms

    def remember(self, request, principal, **kw):
        """ Return a set of headers suitable for 'remembering' the
        principal named ``principal`` when set in a response.  An
        individual authentication policy and its consumers can decide
        on the composition and meaning of **kw. """
        return []

    def forget(self, request):
        """ Return a set of headers suitable for 'forgetting' the
        current user on subsequent requests. """
        return []

def main(global_config, **settings):
    """ This function returns a WSGI application.

    It is usually called by the PasteDeploy framework during
    ``paster serve``.
    """
    settings = dict(settings)
    config = Configurator(settings=settings)
    config.set_session_factory(session_factory_from_settings(settings))

    config.set_authentication_policy(GoogleAuthPolicy(settings))
    config.set_authorization_policy(ACLAuthorizationPolicy())

    DefaultRootFactory.__acl__ = [
        (pyramid.security.Allow, 'admin', pyramid.security.ALL_PERMISSIONS),
        (pyramid.security.Allow, pyramid.security.Authenticated, 'logged_in'),
    ]

    config.include('velruse.providers.google_hybrid')
    config.add_google_hybrid_login(attrs=['email'],
                                   realm=settings.get('velruse.google.realm'))

    engine = engine_from_config(settings, prefix='sqlalchemy.')
    # Create the schema if necessary
    from .models import Base
    Base.metadata.create_all(bind=engine)

    config.registry.dbmaker = sessionmaker(bind=engine,
                                           extension=ZopeTransactionExtension())
    config.add_request_method(db, reify=True)

    config.add_jinja2_search_path("mathclass:templates")

    cache_age = settings.get('pyramid.cache_max_age')
    if cache_age is not None:
        cache_age = int(cache_age)
    config.add_static_view('static', 'static', cache_max_age=cache_age)
    config.add_route('root', '/')
    config.add_route('upload', '/upload')
    config.add_route('delete', r'/delete/{id:\d+}')
    config.add_route('talks', '/_fragment/')
    config.add_route('talk', r'/_fragment/talk/{id:\d+}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
