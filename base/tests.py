from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm, MyUserCreationForm

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpassword'
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_user_email(self):
        self.assertEqual(self.user.email, 'testuser@example.com')

class TopicModelTest(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(name='Test Topic')

    def test_topic_str(self):
        self.assertEqual(str(self.topic), 'Test Topic')

class RoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpassword'
        )
        self.topic = Topic.objects.create(name='Test Topic')
        self.room = Room.objects.create(
            host=self.user, topic=self.topic, name='Test Room', description='Test Description'
        )

    def test_room_str(self):
        self.assertEqual(str(self.room), 'Test Room')

    def test_room_fields(self):
        self.assertEqual(self.room.host, self.user)
        self.assertEqual(self.room.topic, self.topic)
        self.assertEqual(self.room.name, 'Test Room')
        self.assertEqual(self.room.description, 'Test Description')

class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpassword'
        )
        self.topic = Topic.objects.create(name='Test Topic')
        self.room = Room.objects.create(
            host=self.user, topic=self.topic, name='Test Room'
        )
        self.message = Message.objects.create(
            user=self.user, room=self.room, body='Test Message Body'
        )

    def test_message_str(self):
        self.assertEqual(str(self.message), 'Test Message Body')

    def test_message_fields(self):
        self.assertEqual(self.message.user, self.user)
        self.assertEqual(self.message.room, self.room)
        self.assertEqual(self.message.body, 'Test Message Body')


User = get_user_model()

class ViewsTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpassword'
        )
        self.admin_user = User.objects.create_superuser(
            username='adminuser', email='adminuser@example.com', password='adminpassword'
        )
        self.client = Client()

        # Create test data
        self.topic = Topic.objects.create(name='Test Topic')
        self.room = Room.objects.create(
            host=self.admin_user, topic=self.topic, name='Test Room', description='Test Description'
        )
        self.message = Message.objects.create(
            user=self.user, room=self.room, body='Test Message Body'
        )

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')

    def test_logout_user(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/login_register.html')

        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword',
            'password2': 'newpassword',
        })
        print(response.content)  # Debug response content
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/home.html')

    def test_room_page(self):
        response = self.client.get(reverse('room', args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/room.html')

        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.post(reverse('room', args=[self.room.id]), {
            'body': 'Another message'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('room', args=[self.room.id]))

    def test_user_profile(self):
        response = self.client.get(reverse('user-profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/profile.html')

    def test_create_room(self):
        self.client.login(email='adminuser@example.com', password='adminpassword')
        response = self.client.get(reverse('create-room'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/room_form.html')

        response = self.client.post(reverse('create-room'), {
            'name': 'New Room',
            'topic': self.topic.id,
            'description': 'New Room Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_update_room(self):
        self.client.login(email='adminuser@example.com', password='adminpassword')
        response = self.client.get(reverse('update-room', args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/room_form.html')

        response = self.client.post(reverse('update-room', args=[self.room.id]), {
            'name': 'Updated Room Name',
            'topic': self.topic.id,
            'description': 'Updated Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_delete_room(self):
        self.client.login(email='adminuser@example.com', password='adminpassword')
        response = self.client.get(reverse('delete-room', args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/delete.html')

        response = self.client.post(reverse('delete-room', args=[self.room.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_delete_message(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.get(reverse('delete-message', args=[self.message.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/delete.html')

        response = self.client.post(reverse('delete-message', args=[self.message.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_update_user(self):
        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.get(reverse('update-user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/update-user.html')

        response = self.client.post(reverse('update-user'), {
            'name': 'Updated Name',
            'email': 'updatedemail@example.com',
            'bio': 'Updated bio'
        })
        print(response.content)  # Debug response content
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user-profile', args=[self.user.id]))

    def test_topics_page(self):
        response = self.client.get(reverse('topics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/topics.html')

    def test_activity_page(self):
        response = self.client.get(reverse('activity'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/activity.html')

