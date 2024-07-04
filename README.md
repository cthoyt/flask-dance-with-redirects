# flask-dance-with-redirects

This repository gives an example of how to extend [Flask-Dance](https://github.com/singingwolfboy/flask-dance)
to handle URL redirects when doing the OAuth2 dance for you.

First, you'll need to get API credentials for ORCID at https://orcid.org/developer-tools
and set up a redirect for https://0.0.0.0:8775/login/orcid/authorized.

Second, you'll need to clone the repository, install requirements, and create
security credentials to get your local server to (begrudgingly) run HTTPS:

```shell
git clone https://github.com/cthoyt/flask-dance-with-redirects.git
cd flask-dance-with-redirects
python -m pip install -r requirements.txt

# needed to make appropriate security credentials
brew install mkcert
brew install nss
mkcert localhost 127.0.0.1 ::1
mkcert -install

python app.py
```

Finally, navigate to https://0.0.0.0:8775 to see the dance.

You can look inside `app.py` for more detailed instructions on what's going on.
