# services/users/project/tests/test_auth.py


import json
import unittest

from flask import current_app
from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestAuthBlueprint(BaseTestCase):
    def test_user_registration(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'justatest',
                    'email': 'test@test.com',
                    'password': '123456',
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_user_registration_duplicate_email(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'michael',
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That user already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_duplicate_username(self):
        add_user('michael', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'michael',
                    'email': 'test@test2.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That user already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({}),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_no_username(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_no_email(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'michael',
                    'password': 'test'
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_registration_invalid_json_keys_no_password(self):
        with self.client:
            response = self.client.post(
                '/auth/register',
                data=json.dumps({
                    'username': 'michael',
                    'email': 'test@test.com'
                }),
                content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_registered_user_login(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertTrue(data['auth_token'])
            self.assertIn('success', data['status'])
            self.assertIn('Successfully logged in.', data['message'])

    def test_not_registered_user_login(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.content_type, 'application/json')
            self.assertIn('fail', data['status'])
            self.assertIn('User does not exist.', data['message'])

    def test_valid_logout(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Successfully logged out.', data['message'])
            self.assertIn('success', data['status'])

    def test_invalid_logout_expired_token(self):
        add_user('test', 'test@test.com', 'test')
        current_app.config['TOKEN_EXPIRATION_SECONDS'] = -1
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn('Signature expired. Please log in again.',
                          data['message'])
            self.assertIn('fail', data['status'])

    def test_invalid_logout(self):
        response = self.client.get(
            '/auth/logout',
            headers={'Authorization': f'Bearer invalid'}
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token. Please log in again.', data['message'])
        self.assertIn('fail', data['status'])

    def test_user_status(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['data'] is not None)
            self.assertEqual(data['data']['username'], 'test')
            self.assertEqual(data['data']['email'], 'test@test.com')
            self.assertTrue(data['data']['active'])
            self.assertFalse(data['data']['admin'])
            self.assertEqual(response.status_code, 200)

    def test_invalid_status(self):
        with self.client:
            response = self.client.get(
                '/auth/status',
                headers={'Authorization': 'Bearer invalid'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 401)
            self.assertIn('fail', data['status'])
            self.assertIn('Invalid token. Please log in again',
                          data['message'])

    def test_invalid_logout_inactive(self):
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.active = False
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test',
                }),
                content_type='application/json',
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f"Bearer {token}"}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    def test_invalid_status_inactive(self):
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.active = False
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(
                '/auth/logout',
                headers={'Authorization': f"Bearer {token}"}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
