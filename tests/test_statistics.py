'''
Tests that we can load the index page
'''

from __future__ import print_function


def test_two_books(two_books_ten_cards_each_client):
    '''
    Checks that two books show two rows of all genesis
    '''
    response = two_books_ten_cards_each_client.get('/stats/')
    assert response.status_code == 200

    # 1 header row + 2 book row
    assert response.data.count('<tr>') == 3


def test_one_book(one_book_twenty_cards_client):
    '''
    Checks that one book shows one row of all genesis
    '''
    response = one_book_twenty_cards_client.get('/stats/')
    assert response.status_code == 200

    # 1 header row + 1 book row
    assert response.data.count('<tr>') == 2


def test_redirects_without_slash(empty_client):
    '''
    When a client visits /stats, I expect it to forward them to /stats/.
    '''
    response = empty_client.get('/stats')
    assert response.status == '301 MOVED PERMANENTLY'
    assert response.headers['Location'].endswith('/stats/')
