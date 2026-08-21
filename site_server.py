from flask import Flask, send_from_directory, abort, redirect
from site_manager import get_site, is_site_active

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>CyberQueen AI</h1>
    <p>Website service is running.</p>
    """


@app.route("/site/<site_key>")
def website_redirect(site_key):

    return redirect(f"/site/{site_key}/")


@app.route("/site/<site_key>/")
def website_home(site_key):

    site = get_site(site_key)

    if not site:
        return """
        <h1>Website Not Found</h1>
        <p>This website does not exist.</p>
        """, 404

    if not is_site_active(site_key):
        return """
        <h1>Website Expired</h1>
        <p>This website subscription has expired.</p>
        """, 403

    folder = site[5]

    return send_from_directory(
        folder,
        "index.html"
    )


@app.route("/site/<site_key>/<path:filename>")
def website_file(site_key, filename):

    site = get_site(site_key)

    if not site:
        abort(404)

    if not is_site_active(site_key):
        return """
        <h1>Website Expired</h1>
        <p>This website subscription has expired.</p>
        """, 403

    folder = site[5]

    return send_from_directory(
        folder,
        filename
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
