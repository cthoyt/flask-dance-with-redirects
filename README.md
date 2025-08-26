# flask-dance-with-redirects

This repository gives an example of how to extend [Flask-Dance](https://github.com/singingwolfboy/flask-dance)
to handle URL redirects when doing the OAuth2 dance for you.

There's a quick note in https://flask-dance.readthedocs.io/en/latest/understanding-the-magic.html#finishing-the-dance
on how this can work in a different way, but it seems a bit magic. This demo is a bit more explicit and contains
a full example!

First, you'll need to get API credentials for ORCID at https://orcid.org/developer-tools
and set up a redirect for https://0.0.0.0:8775/login/orcid/authorized. You can swap
out many different OAuth2 sources by using Flask-Dance - ORCID is just for demo purposes.

Second, you'll need to clone the repository, install requirements, and create
security credentials to get your local server to (begrudgingly) run HTTPS:

```shell
git clone https://github.com/cthoyt/flask-dance-with-redirects.git
cd flask-dance-with-redirects

# needed to make appropriate security credentials
brew install mkcert
brew install nss
mkcert localhost 127.0.0.1 ::1
mkcert -install

uv run app.py
```

Finally, navigate to https://0.0.0.0:8775 to see the dance.

You can look inside `app.py` for more detailed instructions on what's going on.
