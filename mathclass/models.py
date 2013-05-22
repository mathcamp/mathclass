"""
Models for the database and for form validation
"""
import colander
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Unicode, Integer, Date, UnicodeText

Base = declarative_base() # pylint: disable=C0103

def strip_whitespace(value):
    """ Strip whitespace off a string value """
    if value is colander.null:
        return value
    return value.strip(' \t\n\r')

def date_validator(node, value):
    """ Make sure the date is formatted properly """
    parts = value.split('/')
    if len(parts) != 3:
        raise colander.Invalid(node, 'Date is not in MM/DD/YYYY format!')
    for part in parts:
        if not part.isdigit():
            raise colander.Invalid(node, 'Date is not a number!')

class TalkForm(colander.MappingSchema):
    """ Colander model for validating the Talk data type """
    title = colander.SchemaNode(colander.String(), preparer=strip_whitespace,
                                validator=colander.Length(1))
    author = colander.SchemaNode(colander.String(), preparer=strip_whitespace,
                                validator=colander.Length(1))
    description = colander.SchemaNode(colander.String(),
                                      preparer=strip_whitespace,
                                      validator=colander.Length(1))
    content = colander.SchemaNode(colander.String(), preparer=strip_whitespace,
                                validator=colander.Length(1))
    date = colander.SchemaNode(colander.String(), preparer=strip_whitespace,
                                validator=date_validator)


class Talk(Base):
    """ A talk that was given """
    __tablename__ = 'talks'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(255), unique=True)
    author = Column(Unicode(255))
    description = Column(UnicodeText())
    content = Column(UnicodeText())
    date = Column(Date())

    def __init__(self, title, author, description, date, content):
        self.title = title
        self.author = author
        self.description = description
        self.date = date
        self.content = content

    @classmethod
    def create_test_obj(cls, **kwargs):
        """ Create a Talk for testing purposes """
        from datetime import date
        return Talk(kwargs.get('title', u'test_title'),
                    kwargs.get('author', u'test_author'),
                    kwargs.get('description', u'test_description'),
                    kwargs.get('date', date(2012, 10, 17)),
                    kwargs.get('content', u'test_content'))
