#!/usr/bin/env python
# -*- coding: utf-8 -*-
from CTFd.models import Users
from CTFd.utils import set_config
from tests.helpers import create_ctfd, destroy_ctfd, login_with_mlc, register_user


def test_num_users_oauth_limit():
    """Only num_users users can be created even via MLC"""
    app = create_ctfd()
    app.config.update(
        {
            "OAUTH_CLIENT_ID": "ctfd_client",
            "OAUTH_CLIENT_SECRET": "SAhU01UDmyY7AHFH5B47o3L0qIAQLQkf",
            "OAUTH_AUTHORIZATION_ENDPOINT": "http://0.0.0.0:8080/realms/master/protocol/openid-connect/auth",
            "OAUTH_TOKEN_ENDPOINT": "http://0.0.0.0:8080/realms/master/protocol/openid-connect/token",
            "OAUTH_API_ENDPOINT": "http://0.0.0.0:8080/realms/master/protocol/openid-connect/userinfo",
        }
    )
    with app.app_context():
        register_user(app)
        # There should be the admin and our registered user
        assert Users.query.count() == 2
        set_config("num_users", 1)

        # This registration should fail and we should still have 2 users
        login_with_mlc(
            app,
            name="foobarbaz",
            email="foobarbaz@a.com",
            oauth_id=111,
            scope="profile",
            raise_for_error=False,
        )
        assert Users.query.count() == 2

        # We increment num_users to 2 and then login again
        set_config("num_users", 2)
        login_with_mlc(
            app,
            name="foobarbaz",
            email="foobarbaz@a.com",
            oauth_id=111,
            scope="profile",
        )
        # The above login should have succeeded
        assert Users.query.count() == 3
    destroy_ctfd(app)
