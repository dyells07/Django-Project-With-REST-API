# yourapp/factories.py
import factory
from factory.django import DjangoModelFactory
from .models import User, Topic, Room, Message

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')

class TopicFactory(DjangoModelFactory):
    class Meta:
        model = Topic

    name = factory.Sequence(lambda n: f'Topic {n}')

class RoomFactory(DjangoModelFactory):
    class Meta:
        model = Room

    host = factory.SubFactory(UserFactory)
    topic = factory.SubFactory(TopicFactory)
    name = factory.Sequence(lambda n: f'Room {n}')
    description = factory.Faker('text')

class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message

    user = factory.SubFactory(UserFactory)
    room = factory.SubFactory(RoomFactory)
    body = factory.Faker('text')
