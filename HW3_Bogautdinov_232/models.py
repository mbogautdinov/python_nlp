# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ARTICLE(db.Model):
    __tablename__ = 'ARTICLE'

    articleID = Column(Integer, primary_key=True)
    title = Column(Text)
    pubDate = Column(Text)
    link = Column(Text)
    text = Column(Text)

    AUTHOR = relationship('AUTHOR', secondary='AUTHOR_ARTICLE')
    TAG = relationship('TAG', secondary='TAG_ARTICLE')


class AUTHOR(db.Model):
    __tablename__ = 'AUTHOR'

    authorID = Column(Integer, primary_key=True)
    name = Column(Text)


class TAG(db.Model):
    __tablename__ = 'TAG'

    tagID = Column(Integer, primary_key=True)
    name = Column(Text)


t_AUTHOR_ARTICLE = Table(
    'AUTHOR_ARTICLE', db.metadata,
    Column('authorID', ForeignKey('AUTHOR.authorID'), primary_key=True),
    Column('articleID', ForeignKey('ARTICLE.articleID'), primary_key=True)
)


t_TAG_ARTICLE = Table(
    'TAG_ARTICLE', db.metadata,
    Column('tagID', ForeignKey('TAG.tagID'), primary_key=True),
    Column('articleID', ForeignKey('ARTICLE.articleID'), primary_key=True)
)