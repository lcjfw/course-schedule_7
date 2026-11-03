import json,copy
from django.test import TestCase,Client
from .views import DEFAULT
from django.contrib.auth import get_user_model
class PagesTests(TestCase):
 def setUp(self):
  self.user=get_user_model().objects.create_user(username='tester',password='Sample-pass-735!')
  self.client.force_login(self.user)

 def test_pages(self):
  for path,text in [('/','個人課表'),('/cla/','個人課表'),('/courses/','選課資訊'),('/focus/','套用時間')]:
   self.assertContains(self.client.get(path),text)
 def test_default_and_persist(self):
  a=self.client.get('/api/schedule/').json();self.assertEqual(len(a['state']['courses']),10)
  a['state']['courses'][0]['name']='已修改課程'
  self.assertEqual(self.client.post('/api/schedule/',json.dumps(a),content_type='application/json').status_code,200)
  self.assertEqual(self.client.get('/api/schedule/').json()['state']['courses'][0]['name'],'已修改課程')
 def test_isolation(self):
  a=self.client.get('/api/schedule/').json();a['state']['courses']=[]
  self.client.post('/api/schedule/',json.dumps(a),content_type='application/json')
  other=get_user_model().objects.create_user(username='other',password='Sample-pass-735!');c=Client();c.force_login(other)
  self.assertEqual(len(c.get('/api/schedule/').json()['state']['courses']),10)
 def test_overlap_and_invalid(self):
  a=self.client.get('/api/schedule/').json();a['state']['courses'].append({**a['state']['courses'][0],'id':'other'})
  self.assertEqual(self.client.post('/api/schedule/',json.dumps(a),content_type='application/json').status_code,400)
  self.assertEqual(len(self.client.get('/api/schedule/').json()['state']['courses']),10)
  self.assertEqual(self.client.post('/api/schedule/','[]',content_type='application/json').status_code,400)
 def test_stale_version(self):
  a=self.client.get('/api/schedule/').json()
  self.assertEqual(self.client.post('/api/schedule/',json.dumps(a),content_type='application/json').status_code,200)
  self.assertEqual(self.client.post('/api/schedule/',json.dumps(a),content_type='application/json').status_code,409)
 def test_csrf(self):
  c=Client(enforce_csrf_checks=True);c.force_login(self.user);c.get('/')
  a=c.get('/api/schedule/').json()
  self.assertEqual(c.post('/api/schedule/',json.dumps(a),content_type='application/json').status_code,403)
  self.assertEqual(c.post('/api/schedule/',json.dumps(a),content_type='application/json',HTTP_X_CSRFTOKEN=c.cookies['csrftoken'].value).status_code,200)

 def test_create_update_delete_round_trip(self):
  a=self.client.get('/api/schedule/').json()
  course={**a['state']['courses'][0],'id':'demo-added','name':'測試課程','day':6,'startSlot':1,'endSlot':1}
  a['state']['courses'].append(course)
  def save(payload):
   response=self.client.post('/api/schedule/',json.dumps(payload),content_type='application/json')
   self.assertEqual(response.status_code,200)
   return self.client.get('/api/schedule/').json()
  a=save(a);self.assertEqual(len(a['state']['courses']),11)
  a['state']['courses'][-1]['name']='修改成功';a=save(a)
  self.assertEqual(a['state']['courses'][-1]['name'],'修改成功')
  a['state']['courses']=[c for c in a['state']['courses'] if c['id']!='demo-added'];a=save(a)
  self.assertEqual(len(a['state']['courses']),10)
  from .models import Schedule
  self.assertEqual(Schedule.objects.get().state,a['state'])

class AuthTests(TestCase):
 def test_anonymous_cannot_read_or_write(self):
  for path in ['/','/courses/','/focus/']:
   self.assertRedirects(self.client.get(path),'/login/?next='+path)
  self.assertEqual(self.client.get('/api/schedule/').status_code,401)
  self.assertEqual(self.client.post('/api/schedule/','{}',content_type='application/json').status_code,401)
 def test_signup_login_logout_and_cross_browser(self):
  password='Course-Study-794!'
  self.assertRedirects(self.client.post('/signup/',{'username':'student','password1':password,'password2':password}),'/')
  user=get_user_model().objects.get(username='student')
  self.assertTrue(user.check_password(password));self.assertNotEqual(user.password,password)
  a=self.client.get('/api/schedule/').json();a['state']['courses'][0]['name']='我的課程'
  self.client.post('/api/schedule/',json.dumps(a),content_type='application/json')
  self.assertEqual(self.client.get('/logout/').status_code,405)
  self.assertRedirects(self.client.post('/logout/'),'/login/')
  self.assertContains(self.client.post('/login/',{'username':'student','password':'bad'}),'errorlist')
  other=Client();self.assertRedirects(other.post('/login/',{'username':'student','password':password}),'/')
  self.assertEqual(other.get('/api/schedule/').json()['state']['courses'][0]['name'],'我的課程')
 def test_claim_legacy_only_for_same_browser(self):
  from .models import Schedule
  session=self.client.session;session.save()
  Schedule.objects.create(browser_key=session.session_key,state={**copy.deepcopy(DEFAULT),'courses':[]})
  self.client.post('/signup/',{'username':'legacy','password1':'Course-Study-794!','password2':'Course-Study-794!'})
  self.assertEqual(self.client.get('/api/schedule/').json()['state']['courses'],[])
 def test_auth_forms_require_csrf(self):
  c=Client(enforce_csrf_checks=True)
  self.assertEqual(c.post('/login/',{}).status_code,403)
  self.assertEqual(c.post('/signup/',{}).status_code,403)
