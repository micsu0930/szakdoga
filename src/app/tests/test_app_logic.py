import pytest
from app import update_nav
from dash import html

def test_update_nav_authenticated(sample_auth_data):
    nav_links = update_nav(sample_auth_data)
    
    # Check if links for authenticated users are present
    hrefs = [link.href for link in nav_links if isinstance(link, html.A)]
    assert "/dashboard" in hrefs
    assert "/gallery" in hrefs
    assert "/logout" in hrefs
    assert "/login" not in hrefs

def test_update_nav_unauthenticated():
    nav_links = update_nav(None)
    
    hrefs = [link.href for link in nav_links if isinstance(link, html.A)]
    assert "/login" in hrefs
    assert "/register" in hrefs
    assert "/dashboard" not in hrefs

def test_update_nav_empty_token():
    nav_links = update_nav({"access_token": ""})
    
    hrefs = [link.href for link in nav_links if isinstance(link, html.A)]
    assert "/login" in hrefs
    assert "/dashboard" not in hrefs
