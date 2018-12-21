'''
Tests that we can load the study page in various conditions
'''

from __future__ import print_function


def test_redirect(empty_client):
    """
    Make sure we redirect from no-trailing-slash to with-trailing-slash
    """

    response = empty_client.get('/cards')
    assert response.status_code == 301
    assert response.headers['Location'].endswith('/cards/')
