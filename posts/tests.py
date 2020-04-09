from django.test import TestCase
from django.test import Client
from .models import User
from . import views
from django.urls import reverse


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", password="12345")
    
    def test_profile(self):  # проверка на создание персональной страницы   
        response = self.client.post('/auth/signup/', {'first_name': "Alexey", 
                                    'last_name': 'Volkov', 'username': 'AGV', 'email': 'volkov@mail.ru', 
                                    "password1": "123qwe12", 'password2': '123qwe12'}, follow=True)
        response = self.client.get("/AGV/")
        self.assertEqual(response.status_code, 200)        

    def test_new(self):
        self.client.login(username='sarah', password='12345')  
        response = self.client.post(reverse('new_post'), {'text': 'FirstPost'}, follow=True)  # авторизованный пользователь может опубликовать пост
        response = self.client.get('/')  # проверка на публикацию поста
        self.assertContains(response, text='FirstPost', status_code=200)
        response = self.client.get("/sarah/")
        self.assertContains(response, text='FirstPost', status_code=200)
        response = self.client.get("/sarah/1/")
        self.assertContains(response, text='FirstPost', status_code=200)                              
        
    def test_edit(self):    
        self.client.login(username='sarah', password='12345')
        self.client.post(reverse('new_post'), {'text': 'FirstPost'}, follow=True)
        response = self.client.post(reverse('post_edit', kwargs={'username': 'sarah', 'post_id': '1'}),
                                           {'text': 'EditPost'}, follow=True)  # проверка на изменение поста
        response = self.client.get('/')
        self.assertContains(response, text='EditPost', status_code=200)
        response = self.client.get("/sarah/")
        self.assertContains(response, text='EditPost', status_code=200)
        response = self.client.get("/sarah/1/")
        self.assertContains(response, text='EditPost', status_code=200)


class test_not_auth(TestCase):  # Неавторизованный посетитель не может опубликовать пост
    def setUp(self):
        self.client = Client()

    def test_redirect(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/')


#class test_image(TestCase):
    #def setUp(self):
        #self.client = Client()
        #self.user = User.objects.create_user(
                        #username="sarah", email="connor.s@skynet.com", password="12345")

    #def test_img(self):
        #self.client.login(username='sarah', password='12345')
        #with open('file.ext') as fp:
            #c.post(reverse('new_post'), {'text': 'FirstPost'}, follow=True)


class test_follow(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.user1 = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", password="12345")
        self.client2 = Client()
        self.user2 = User.objects.create_user(
                        username="volkov", email="volkov@skynet.com", password="12345") 
    
    def test_flw(self):
        self.client1.login(username='sarah', password='12345')
        self.client2.login(username='volkov', password='12345')
        self.client2.post(reverse('new_post'), {'text': 'Текст поста'}, follow=True)
        self.client1.get(reverse('profile_follow', kwargs={'username': "volkov"}))  # Авторизованный пользователь может подписываться на других пользователей 
        response = self.client1.get(reverse('follow_index')) 
        self.assertContains(response, text='Текст поста', status_code=200) # Новая запись пользователя появляется в ленте тех, кто на него подписан
        self.client1.get(reverse('profile_unfollow', kwargs={'username': "volkov"}))  # Авторизованный пользователь может удалять других пользователей из подписок.
        self.assertContains(response, text='Текст поста', status_code=200)  # Новая запись пользователя не появляется в ленте тех, кто не подписан на него.


class test_comment(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", password="12345")

    def test_cmnt(self):
        self.client.login(username='sarah', password='12345')                    
