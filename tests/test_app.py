from fastapi.testclient import TestClient
import urllib.parse
import copy

from src import app as _app

client = TestClient(_app.app)

# Keep a copy of the original activities so tests can restore state between runs
ORIGINAL_ACTIVITIES = copy.deepcopy(_app.activities)

def teardown_function(func):
    # restore original in-memory data
    _app.activities.clear()
    _app.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    # basic sanity
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "tester@example.com"

    # ensure starting state: email not present
    assert email not in _app.activities[activity]["participants"]

    # sign up
    url = f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    res = client.post(url)
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")
    assert email in _app.activities[activity]["participants"]

    # duplicate signup should fail
    res_dup = client.post(url)
    assert res_dup.status_code == 400

    # unregister
    url_unreg = f"/activities/{urllib.parse.quote(activity)}/unregister?email={urllib.parse.quote(email)}"
    res_unreg = client.delete(url_unreg)
    assert res_unreg.status_code == 200
    assert email not in _app.activities[activity]["participants"]

    # unregister again should 404
    res_unreg2 = client.delete(url_unreg)
    assert res_unreg2.status_code == 404
