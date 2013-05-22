"""
Unit tests for math class
"""
import unittest
from pyramid import testing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Talk


class IntegrationTests(unittest.TestCase):
    """ Integration tests """
    def setUp(self):
        testing.setUp()
        self.engine = create_engine('sqlite:///:memory:')
        self.session = sessionmaker(bind=self.engine)()
        Base.metadata.create_all(self.engine)
        self.request = testing.DummyRequest()
        self.request.db = self.session

    def tearDown(self):
        testing.tearDown()
        self.session.close()
        Base.metadata.reflect(self.engine)
        Base.metadata.drop_all(self.engine)

    def test_get_talk(self):
        """ get_talk should return the talk by id """
        from mathclass.views import get_talk
        test_talk = Talk.create_test_obj()
        self.session.add(test_talk)
        self.session.commit()
        self.request.matchdict['id'] = test_talk.id
        response = get_talk(self.request)
        self.assertEqual(response, {'talk':test_talk})

    def test_upload_talk(self):
        """ After uploading, a talk should be in the database """
        from mathclass.views import do_upload
        self.request.POST = {'title':'test_title', 'author':'test_author',
                             'description':'test_description',
                             'content':'test_content', 'date':'5/5/2012'}
        do_upload(self.request)
        talks = self.session.query(Talk).all()
        self.assertEqual(len(talks), 1)
        talk = self.session.query(Talk).first()
        self.assertEqual(talk.title, self.request.POST['title'])

    def test_upload_talk_fail(self):
        """ If uploading the talk fails, it should not be in the database """
        from mathclass.views import do_upload
        self.request.POST = {}
        do_upload(self.request)
        talks = self.session.query(Talk).all()
        self.assertEqual(len(talks), 0)
