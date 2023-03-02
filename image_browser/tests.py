import shutil
import time
from datetime import datetime
from unittest import skip

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APIClient

from image_browser.models import PlanTier, ThumbnailSize, User, AppUser, ImageInstance

TEST_DIR = 'test_data'

username = 'test'
password = 'Krowadzika'


def create_test_user_with_plan(plan: PlanTier, username=username, password=password) -> User:
    user = User.objects.create(username=username, password=password)
    AppUser.objects.create(user=user, plan=plan)
    return User.objects.get(username=username)


def upload_image_request(image_path, image_name, client) -> Response:
    with open(image_path, 'rb') as data:
        upload_json = {
            'name': image_name,
            'image_file': data
        }
        return client.post('/images/upload', upload_json, format='multipart')


def create_temp_link(image_name, client, seconds) -> Response:
    url = get_create_link_url(image_name)
    response = client.post(url, {'expires_seconds': seconds}, format='json')
    return response


def get_create_link_url(image_name) -> str:
    image_id = ImageInstance.objects.get(name=image_name).id
    return f'/make_temp/{image_id}/'


class BuiltinPlanTiersTestCase(TestCase):

    def test_builtin_thumbnail_sizes(self):
        th200: ThumbnailSize = ThumbnailSize.objects.get(height=200)
        th400: ThumbnailSize = ThumbnailSize.objects.get(height=400)
        self.assertIsNotNone(th200)
        self.assertEquals(th200.height, 200)
        self.assertEquals(th200.width, 0)

        self.assertIsNotNone(th400)
        self.assertEquals(th400.height, 400)
        self.assertEquals(th400.width, 0)

    def test_basic_plan_available(self):
        th200: ThumbnailSize = ThumbnailSize.objects.get(height=200)

        basic_obj: PlanTier = PlanTier.objects.get(name='Basic')
        self.assertIsNotNone(basic_obj, 'Basic does not exist')
        self.assertEquals(basic_obj.name, 'Basic', 'Basic plan has wrong name')
        self.assertFalse(basic_obj.show_original_link, 'Basic can see original link')
        self.assertFalse(basic_obj.create_expiring_link, 'Basic can create expiring link')
        self.assertSetEqual(set(basic_obj.thumbnail_sizes.all()), {th200})

    def test_premium_plan_available(self):
        th200: ThumbnailSize = ThumbnailSize.objects.get(height=200)
        th400: ThumbnailSize = ThumbnailSize.objects.get(height=400)

        premium_obj: PlanTier = PlanTier.objects.get(name='Premium')
        self.assertIsNotNone(premium_obj, 'Premium does not exist')
        self.assertEquals(premium_obj.name, 'Premium', 'Premium plan has wrong name')
        self.assertTrue(premium_obj.show_original_link, 'Premium can see original link')
        self.assertFalse(premium_obj.create_expiring_link, 'Premium can create expiring link')
        self.assertSetEqual(set(premium_obj.thumbnail_sizes.all()), {th200, th400})

    def test_enterprise_plan_available(self):
        th200: ThumbnailSize = ThumbnailSize.objects.get(height=200)
        th400: ThumbnailSize = ThumbnailSize.objects.get(height=400)
        enter_obj: PlanTier = PlanTier.objects.get(name='Enterprise')
        self.assertIsNotNone(enter_obj, 'Enterprise does not exist')
        self.assertEquals(enter_obj.name, 'Enterprise', 'Enterprise plan has wrong name')
        self.assertTrue(enter_obj.show_original_link, 'Enterprise can see original link')
        self.assertTrue(enter_obj.create_expiring_link, 'Enterprise can create expiring link')
        self.assertSetEqual(set(enter_obj.thumbnail_sizes.all()), {th200, th400})


class CanSeeOriginalLink(TestCase):
    client = None

    def setUp(self) -> None:
        plan: PlanTier = PlanTier.objects.create(name='OrigLink', show_original_link=True,
                                                 create_expiring_link=False)
        user = create_test_user_with_plan(plan)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def tearDown(self):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    @override_settings(THUMBNAIL_NAMER=('easy_thumbnails.namers.default'))
    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_only_name_and_orig_url_after_upload(self):
        response = upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['name'], 'macara')
        self.assertIn('/media/user_test/macara.jpg', response.data['image_url'])
        self.assertEquals(len(response.data), 2)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_name_and_url_in_list(self):
        upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        upload_image_request('staticfiles/rabbit.png', 'rabbit', self.client)
        response = self.client.get('/images/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data[0]['name'], 'macara')
        self.assertIn('/media/user_test/macara.jpg', response.data[0]['image_url'])

        self.assertEquals(response.data[1]['name'], 'rabbit')
        self.assertIn('/media/user_test/rabbit.png', response.data[1]['image_url'])
        self.assertEquals(len(response.data), 2)
        self.assertEquals(len(response.data[0]), 2)


class CanSeeGivenOneThumbnail(TestCase):
    client = None

    def setUp(self) -> None:
        plan: PlanTier = PlanTier.objects.create(name='OrigLink', show_original_link=False,
                                                 create_expiring_link=False)
        ts = ThumbnailSize.objects.create(height=0, width=50)
        plan.thumbnail_sizes.set([ts])

        user = create_test_user_with_plan(plan)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def tearDown(self):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    @override_settings(THUMBNAIL_NAMER='easy_thumbnails.namers.default')
    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_only_thumbnail_url_after_upload(self):
        response = upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['name'], 'macara')
        self.assertIn('/media/user_test/macara.jpg.50x0_q85.jpg', response.data['thumbnail_0x50_url'])
        self.assertEquals(len(response.data), 2)

    @override_settings(THUMBNAIL_NAMER='easy_thumbnails.namers.default')
    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_name_and_url_in_list(self):
        upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        upload_image_request('staticfiles/rabbit.png', 'rabbit', self.client)
        response = self.client.get('/images/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data[0]['name'], 'macara')
        self.assertIn('/media/user_test/macara.jpg.50x0_q85.jpg', response.data[0]['thumbnail_0x50_url'])

        self.assertEquals(response.data[1]['name'], 'rabbit')
        self.assertIn('/media/user_test/rabbit.png.50x0_q85.jpg', response.data[1]['thumbnail_0x50_url'])
        self.assertEquals(len(response.data), 2)
        self.assertEquals(len(response.data[0]), 2)


class CanSeeManyThumbnails(TestCase):
    client = None

    def setUp(self) -> None:
        plan: PlanTier = PlanTier.objects.create(name='OrigLink', show_original_link=False,
                                                 create_expiring_link=False)
        ts = ThumbnailSize.objects.create(height=0, width=50)
        ts1 = ThumbnailSize.objects.create(height=100, width=50)
        plan.thumbnail_sizes.set([ts, ts1])

        user = create_test_user_with_plan(plan)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def tearDown(self):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    @override_settings(THUMBNAIL_NAMER='easy_thumbnails.namers.default')
    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_only_thumbnail_urls_after_upload(self):
        response = upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['name'], 'macara')
        self.assertIn('/media/user_test/macara.jpg.50x0_q85.jpg', response.data['thumbnail_0x50_url'])
        self.assertIn('/media/user_test/macara.jpg.50x100_q85.jpg', response.data['thumbnail_100x50_url'])
        self.assertEquals(len(response.data), 3)

    @override_settings(THUMBNAIL_NAMER='easy_thumbnails.namers.default')
    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_name_and_urls_in_list(self):
        upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        upload_image_request('staticfiles/rabbit.png', 'rabbit', self.client)
        response = self.client.get('/images/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data[0]['name'], 'macara')
        self.assertIn('/media/user_test/macara.jpg.50x0_q85.jpg', response.data[0]['thumbnail_0x50_url'])
        self.assertIn('/media/user_test/macara.jpg.50x100_q85.jpg', response.data[0]['thumbnail_100x50_url'])

        self.assertEquals(response.data[1]['name'], 'rabbit')
        self.assertIn('/media/user_test/rabbit.png.50x0_q85.jpg', response.data[1]['thumbnail_0x50_url'])
        self.assertIn('/media/user_test/rabbit.png.50x100_q85.jpg', response.data[1]['thumbnail_100x50_url'])
        self.assertEquals(len(response.data), 2)
        self.assertEquals(len(response.data[0]), 3)


class CanCreateExpiringLink(TestCase):
    client = None

    def setUp(self) -> None:
        plan: PlanTier = PlanTier.objects.create(name='Test', show_original_link=False,
                                                 create_expiring_link=True)
        user = create_test_user_with_plan(plan)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def tearDown(self):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_only_name_and_expiring_creation_link(self):
        response = upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        image_id = ImageInstance.objects.get(name='macara').id
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data['name'], 'macara')
        self.assertIn(f'/make_temp/{image_id}', response.data['create_expiring_link'])
        self.assertEquals(len(response.data), 2)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_sees_name_and_url_in_list(self):
        upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        macara_id = ImageInstance.objects.get(name='macara').id
        upload_image_request('staticfiles/rabbit.png', 'rabbit', self.client)
        rabbit_id = ImageInstance.objects.get(name='rabbit').id
        response = self.client.get('/images/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data[0]['name'], 'macara')
        self.assertIn(f'/make_temp/{macara_id}', response.data[0]['create_expiring_link'])

        self.assertEquals(response.data[1]['name'], 'rabbit')
        self.assertIn(f'/make_temp/{rabbit_id}', response.data[1]['create_expiring_link'])
        self.assertEquals(len(response.data), 2)
        self.assertEquals(len(response.data[0]), 2)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_create_expiring_link(self):
        upload_image_request('staticfiles/macara.jpg', 'macara', self.client)
        macara_id = ImageInstance.objects.get(name='macara').id
        now = timezone.now()
        response = self.client.post(f'/make_temp/{macara_id}/', {'expires_seconds': 300}, format='json')
        self.assertIsNotNone(response.data['url_hash'])
        self.assertIsNotNone(response.data['expiring_link_url'])
        exp_date = datetime.fromisoformat(response.data['expiration_date'])
        self.assertAlmostEqual((exp_date - now).seconds, 300, 2)
        self.assertEquals(len(response.data), 3)


class ExpiringLinkCreation(TestCase):
    client1 = None
    client2 = None

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def setUp(self) -> None:
        plan1: PlanTier = PlanTier.objects.create(name='Test', show_original_link=False,
                                                  create_expiring_link=True)
        user1 = create_test_user_with_plan(plan1)
        self.client1 = APIClient()
        self.client1.force_authenticate(user=user1)
        upload_image_request('staticfiles/macara.jpg', 'macara', self.client1)

        user2 = create_test_user_with_plan(plan1, 'test2', 'Krowadzika')
        self.client2 = APIClient()
        self.client2.force_authenticate(user=user2)

    def tearDown(self):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_owner_can_enter_link_creation(self):
        response = create_temp_link('macara', self.client1, 300)
        self.assertEquals(response.status_code, 201)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_non_owner_cannot_enter_link_creation(self):
        response = create_temp_link('macara', self.client2, 300)
        self.assertEquals(response.status_code, 403)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_cannot_less_expiration_than_300(self):
        response = create_temp_link('macara', self.client1, 200)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['expires_seconds'][0],
                          'Seconds must be value between 300 and 30000.')

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_cannot_more_expiration_than_30000(self):
        response = create_temp_link('macara', self.client1, 40000)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['expires_seconds'][0],
                          'Seconds must be value between 300 and 30000.')


class ExpiringLink(TestCase):
    client = None
    client1 = None
    link = None

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def setUp(self) -> None:
        plan1: PlanTier = PlanTier.objects.create(name='Test', show_original_link=False,
                                                  create_expiring_link=True)
        user1 = create_test_user_with_plan(plan1)
        self.client1 = APIClient()
        self.client1.force_authenticate(user=user1)
        upload_image_request('staticfiles/macara.jpg', 'macara', self.client1)
        self.link = create_temp_link('macara', self.client1, 300).data['expiring_link_url']
        self.client = APIClient()

    def tearDown(self):
        shutil.rmtree(TEST_DIR, ignore_errors=True)

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_any_can_see_valid_link(self):
        response = self.client.get(self.link)
        self.assertEquals(response.status_code, 200)

    @skip('This test takes 5 minutes and should be run when needed')
    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_cannot_see_after_expiration(self):
        response = self.client.get(self.link)
        self.assertEquals(response.status_code, 200)
        time.sleep(301)
        response = self.client.get(self.link)
        self.assertEquals(response.status_code, 404)


