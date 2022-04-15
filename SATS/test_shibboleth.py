import os
import random
import string
import time

from bs4 import BeautifulSoup
import pytest

from .uaaclient import UAAClient
from .integration_test import IntegrationTestClient


@pytest.fixture
def config():
    config = {}
    urls = {}
    urls["uaa"] = os.environ["UAA_URL"]
    urls["extras"] = os.environ["EXTRAS_URL"]
    urls["idp"] = os.environ["IDP_URL"]
    for url in urls:
        if not urls[url][0:4] == "http":
            urls[url] = "https://" + urls[url]
    config["urls"] = urls
    config["idp_name"] = os.environ["IDP_NAME"]
    config["uaa_client"] = os.environ["UAA_USER"]
    config["uaa_secret"] = os.environ["UAA_SECRET"]
    return config


@pytest.fixture
def uaa(config):
    uaac = UAAClient(config["urls"]["uaa"], None, verify_tls=True)
    token = uaac._get_client_token(config["uaa_client"], config["uaa_secret"])
    uaac.token = token
    return uaac


@pytest.fixture
def user(uaa, config):
    user = {}
    user["name"] = (
        "noreply+" + "".join(random.choices(string.ascii_lowercase, k=8)) + "@cloud.gov"
    )
    user["password"] = "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=20
        )
    )
    r = uaa.create_user(
        user["name"],
        "unimportant",
        "alsounimportant",
        user["name"],
        password=user["password"],
        origin="cloud.gov",
    )
    uaa.set_temporary_password(
        config["uaa_client"], config["uaa_secret"], user["name"], user["password"]
    )
    yield user
    uaa.delete_user(r["id"])


@pytest.fixture
def unauthenticated(config):
    itc = IntegrationTestClient(
        config["urls"]["extras"],
        config["urls"]["idp"],
        config["urls"]["uaa"],
        config["idp_name"],
    )
    return itc


@pytest.fixture
def authenticated(unauthenticated, user):
    token, changed = unauthenticated.log_in(user["name"], user["password"])
    if changed:
        user["token"] = token
    return unauthenticated


def get_csrf(page_text) -> str:
    page = BeautifulSoup(page_text, features="html.parser")
    csrf = page.find(attrs={"name": "_csrf_token"}).attrs["value"]
    return csrf


@pytest.mark.parametrize("page", ["/invite", "/change-password", "/first-login"])
def test_unauthenticated_pages_redirect(unauthenticated, page, config):
    r = unauthenticated.get_page(page)
    assert r.status_code == 200
    assert r.url == config["urls"]["uaa"] + "/login"


def test_login_no_totp(unauthenticated, config, user):
    # this is the happiest-path test
    # log in to get/set our totp
    token, changed = unauthenticated.log_in(user["name"], user["password"])
    assert changed
    # log out, so log in will work
    unauthenticated.log_out()

    # log in again to make sure we have the right totp
    _, changed = unauthenticated.log_in(user["name"], user["password"], token)
    assert not changed


def test_no_login_with_bad_password(unauthenticated, config, user):
    response = unauthenticated.uaa_pick_idp()
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, features="html.parser")
    form = soup.find("form")
    next_url = form.attrs["action"]
    response = unauthenticated.idp_start_log_in(next_url)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, features="html.parser")
    form = soup.find("form")
    next_url = form.attrs["action"]
    response = unauthenticated.idp_username_password_login(next_url, user["name"], "bad-password")
    assert response.status_code == 200
    assert "invalid username or password" in response.text.lower()


def test_no_login_with_bad_totp(unauthenticated, config, user):
    # log in so we have a user with a good totp seed
    token, changed = unauthenticated.log_in(user["name"], user["password"])
    assert changed
    # log out, so log in will work
    unauthenticated.log_out()

    response = unauthenticated.uaa_pick_idp()
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, features="html.parser")
    form = soup.find("form")
    next_url = form.attrs["action"]
    response = unauthenticated.idp_start_log_in(next_url)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, features="html.parser")
    form = soup.find("form")
    next_url = form.attrs["action"]
    response = unauthenticated.idp_username_password_login(next_url, user["name"], user["password"])
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, features="html.parser")
    form = soup.find("form")
    # the action will look like <url>?execution=e1s5
    first_totp_step = int(form.attrs["action"][-1])
    _, _, response = unauthenticated.idp_totp_login(response.text, totp_seed="asdf")

    soup = BeautifulSoup(response.text, features="html.parser")
    form = soup.find("form")
    second_totp_step = int(form.attrs["action"][-1])
    # the last digit of the execution value increments every time you retry the token
    # this is kind of a silly test, but the token input UI doesn't change if you put in a bad token
    # so this hopefully tests that we actually posted, failed the comparison, and got a response back
    assert first_totp_step + 1 == second_totp_step
    assert "token code from your authentication app" in response.text