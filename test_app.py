import pytest
from app import app

"""Test the homepage route"""


def text_homepage():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b"Render homepage" in response.data


""" Test the signup route"""


def test_signup():
    with app.test_client() as client:
        response = client.post('/signup', data=dict(
            username='testuser',
            name='Test User',
            password='testpassword'
        ), follow_redirects=True)
        assert response.status_code == 200
        assert b"Sign Up!" in response.data


"""Test user login route"""


def test_login():
    with app.test_client() as client:
        response = client.post('/login', data=dic(
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        assert response.status_code == 200
        assert b"Welcome Back!" in response.data


"""Test logout route"""


def test_logout():
    with app.test_client() as client:
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b"You have successfully logged out." in response.data
        assert b"Handle user logout" in response.data


"""Test user profile route"""


def test_user_profile():
    with app.test_client() as client:
        response = client.get('/users/profile/1')
        assert response.status_code == 200
        assert b"Show user profile" in response.data
        assert b"User profile" in response.data


"""Test logout route"""

"""Test delete user route"""
