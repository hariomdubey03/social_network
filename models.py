# coding: utf-8
from sqlalchemy import CHAR, Column, ForeignKey, Integer, String, TIMESTAMP, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class SocialGroup(Base):
    __tablename__ = 'social_groups'

    id = Column(Integer, primary_key=True)
    code = Column(CHAR(36), nullable=False, server_default=text("(uuid())"))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    code = Column(CHAR(36), nullable=False, server_default=text("(uuid())"))
    name = Column(String(100), nullable=False)
    email_address = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    last_used = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP)


class GroupMembership(Base):
    __tablename__ = 'group_memberships'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), index=True)
    group_id = Column(ForeignKey('social_groups.id'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP)

    group = relationship('SocialGroup')
    user = relationship('User')


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    code = Column(CHAR(36), nullable=False, server_default=text("(uuid())"))
    user_id = Column(ForeignKey('users.id'), index=True)
    group_id = Column(ForeignKey('social_groups.id'), index=True)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP)

    group = relationship('SocialGroup')
    user = relationship('User')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    code = Column(CHAR(36), nullable=False, server_default=text("(uuid())"))
    user_id = Column(ForeignKey('users.id'), index=True)
    post_id = Column(ForeignKey('posts.id'), index=True)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP)

    post = relationship('Post')
    user = relationship('User')


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True)
    code = Column(CHAR(36), nullable=False, server_default=text("(uuid())"))
    user_id = Column(ForeignKey('users.id'), index=True)
    post_id = Column(ForeignKey('posts.id'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    deleted_at = Column(TIMESTAMP)

    post = relationship('Post')
    user = relationship('User')
