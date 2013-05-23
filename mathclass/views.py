"""
View for the website
"""
import logging
import velruse
import colander
from datetime import date
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import has_permission, Authenticated
from .models import Talk, TalkForm

LOG = logging.getLogger(__name__)


@view_config(route_name='root', renderer='index.jinja2')
def index(request):
    """ Render the base template """
    return {'logged_in': has_permission('logged_in', request.context, request),
            'can_upload': has_permission('upload', request.context, request),
            }

@view_config(route_name='upload', request_method='POST', renderer='json', permission='upload')
def do_upload(request):
    """ Handle a form upload """
    try:
        appstruct = TalkForm().deserialize(request.POST)
    except colander.Invalid as e:
        return {'status':1, 'errors':e.asdict()}
    title = appstruct['title']
    author = appstruct['author']
    content = appstruct['content']
    desc = appstruct['description']
    month, day, year = [int(s) for s in appstruct['date'].split('/')]
    talk_date = date(year, month, day)
    if request.db.query(Talk).filter_by(title=title).first() is not None:
        return {'status':1, 'errors':
                {'title':'A talk with that name already exists!'}}
    new_talk = Talk(title, author, desc, talk_date, content)
    request.db.add(new_talk)
    return {'status':0, 'msg':'success'}

@view_config(route_name='delete', request_method='DELETE', renderer='json', permission='delete')
def do_delete(request):
    """ Delete a talk """
    talk = request.db.query(Talk).filter_by(id=request.matchdict['id']).first()
    request.db.delete(talk)
    return {'status':0}

@view_config(route_name='talks', renderer='talk_list.jinja2')
def get_talks(request):
    """ Get a list of all talks ordered by date """
    return {'talks':request.db.query(Talk).order_by(Talk.date.desc()).all()}

@view_config(route_name='talk', renderer='talk.jinja2')
def get_talk(request):
    """ Get a single talk by id """
    talk = request.db.query(Talk).filter_by(id=request.matchdict['id']).first()
    return {'talk': talk,
            'can_delete':has_permission('delete', request.context, request),
            }

@view_config(route_name='login')
def do_login(request):
    """ Store the redirect in the session and log in with google """
    if 'next' in request.GET:
        request.session['next'] = request.GET['next']
    raise HTTPFound(location=velruse.login_url(request, 'google'))

@view_config(route_name='logout')
def do_logout(request):
    """ Log the user out """
    request.session.delete()
    raise HTTPFound(location=request.route_url('root'))

@view_config(context='velruse.AuthenticationComplete')
def on_login(request):
    """ Called when a user successfully logs in """
    context = request.context
    email, domain = context.profile['verifiedEmail'].split('@')
    if domain == 'highlig.ht':
        request.session['username'] = email
    next_url = request.session.pop('next', request.route_url('root'))
    raise HTTPFound(location=next_url)

@view_config(context='velruse.AuthenticationDenied')
def on_login_denied(request):
    """ Called when the login is denied """
    raise HTTPFound(location=request.route_url('root'))
