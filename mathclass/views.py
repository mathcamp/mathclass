"""
View for the website
"""
import logging
import colander
from datetime import date
from pyramid.view import view_config
from .models import Talk, TalkForm

LOG = logging.getLogger(__name__)


@view_config(route_name='root', renderer='index.jinja2')
def index(request):
    """ Render the base template """
    return {}

@view_config(route_name='upload', request_method='POST', renderer='json')
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

@view_config(route_name='talks', renderer='talk_list.jinja2')
def get_talks(request):
    """ Get a list of all talks ordered by date """
    return {'talks':request.db.query(Talk).order_by(Talk.date.desc()).all()}

@view_config(route_name='talk', renderer='talk.jinja2')
def get_talk(request):
    """ Get a single talk by id """
    talk = request.db.query(Talk).filter_by(id=request.matchdict['id']).first()
    return {'talk': talk}
