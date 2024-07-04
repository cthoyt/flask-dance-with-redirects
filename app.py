"""
This is a full demo that shows how to set up Flask-Dance
to properly run redirects after OAuth2 authentication
"""

import os

import flask
import pystow
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import redirect, url_for
from flask_dance.contrib.orcid import make_orcid_blueprint, orcid

app = flask.Flask(__name__)

# You need to set the secret key otherwise Flask doesn't
# let you use the `flask.session` object
app.secret_key = os.urandom(8)

# This example uses the OAuth2 provider from ORCID. You can navigate to
# https://orcid.org/developer-tools to get your own credentials, or feel
# free to use one of Flask-Dance's other providers in :mod:`flask_dance.contrib`.
CLIENT_ID = pystow.get_config("orcid", "client_id", raise_on_missing=True)
CLIENT_SECRET = pystow.get_config("orcid", "client_secret", raise_on_missing=True)

# While setting up the redirects on the ORCID developer tools dashboard,
# you will want to point towards where the application is running. Based
# on the way this demo is written, you'll want to put in the following:
#
#   https://0.0.0.0:8775/login/orcid/authorized
HOST = "0.0.0.0"
PORT = 8775

# Because OAuth2 requires a redirect to a server that supports HTTPS,
# we have to spoof it. Run the following shell commands on Mac/Linux
# to make an appropriate key file:
#
#  > brew install mkcert
#  > brew install nss
#  > mkcert localhost 127.0.0.1 ::1
#  > mkcert -install
#
# Then, we have to make sure the filenames are put in the following variables
SSL_KEYFILE = "./localhost+2-key.pem"
SSL_CERTFILE = "./localhost+2.pem"

# Note that Flask Dance has several different OAuth2 providers in
# :mod:`flask_dance.contrib` that all have the same unified interface.
# Each of them has their own `scope` that is necessary, so you'll have
# to read the documentation on their endpoints to figure this out in
# your use case
auth_blueprint = make_orcid_blueprint(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope="/authenticate",
    # This is explicitly showing the default redirect URL that should
    # happen after the dance. Unfortunately, this can't be dynamic, which
    # is why we have to get clever in the next steps. If you don't set
    # the `redirect_url` or the `redirect_to`, it defaults to "/".
    redirect_url="/",
    # If you don't want to specify the redirect URL itself but would rather
    # make it a bit more clever based on the name of the route, you can use
    # `redirect_to` in combination with the route name, same as you'd use in
    # :func:`flask.url_for`.
    # redirect_to="view_home",
)

# Note we're registering on the /login path, which means that we will
# have paths like /login/<consumer name>/authorization. This helps avoid
# conflicts, in case you also have endpoints like /orcid/<orcid_id>.
# Luckily, this doesn't stick anything in the '/' of the blueprint
# (which becomes /login after mounting) so we can pile up below with
# the /login route
app.register_blueprint(auth_blueprint, url_prefix="/login")


@app.route("/login")
def view_login():
    # If there's a URL parameter called `next_url`, get it from the arguments
    # and store it in the session. This is saved for the specific user, so after
    # authentication is over, we can get this information back. We have to do this
    # because the OAuth2 endpoint doesn't do this kind of handling for us.
    next_url = flask.request.args.get(
        "next_url",
        # we're choosing the home route as the default in
        # case no `next_url` is specified.
        default=url_for(view_home.__name__),
    )

    # If we're already authorized, we don't have to do the dance,
    # and can just redirect to the given `next_url`
    if orcid.authorized:
        return redirect(next_url)

    # store the `next_url` in the session, so we can use it later.
    flask.session["next_url"] = next_url

    # after successful login, will redirect to "/" based on the `redirect_to`
    # parameter in the blueprint. When we get there, the `view_home` route
    # has logic for popping the `next_url` off of the session and redirecting
    return redirect(url_for(f"{auth_blueprint.name}.login"))


@app.route("/")
def view_home():
    # Check if a redirect has been stored in the session,
    #  e.g., from before doing the OAuth dance. If found, redirect.
    #  This is implemented in the home endpoint "/" since that's the default
    #  redirect from the Flask-Dance OAuth2 class.
    #
    # An alternative to having this code in the home endpoint is described in
    # https://flask-dance.readthedocs.io/en/latest/understanding-the-magic.html#finishing-the-dance
    if next_url := flask.session.pop("next_url", None):
        return redirect(next_url)

    # If we're not logged in, let's redirect to our wrapped login.
    # We never have to refer to the Flask-Dance blueprint since we've
    # safely wrapped it
    if not orcid.authorized:
        return f"<a href='{url_for(view_login.__name__)}'>Log in with {auth_blueprint.name}</a>"

    return f"Hello, {orcid.token['name']}. You're on the home page!"


@app.route("/page-1")
def view_page_1():
    # This block gets invoked if you directly try to go to this page
    # without authorization. It will log you in then redirect back.
    # Note that the `url_for(view_page_1.__name__)` can also be used in
    # combination with *args and **kwargs!
    if not orcid.authorized:
        return redirect(url_for(view_login.__name__, next_url=url_for(view_page_1.__name__)))

    return f"Hello, {orcid.token['name']}. You're on an extra page!"


if __name__ == "__main__":
    uvicorn.run(
        WsgiToAsgi(app),
        host=HOST,
        port=PORT,
        ssl_keyfile=SSL_KEYFILE,
        ssl_certfile=SSL_CERTFILE,
    )
