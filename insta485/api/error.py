"""
REST API for error_handling.

Returns json object
"""
import hashlib
import flask
import insta485


def report_status(status):
    """Check and report status."""
    if status == 403:
        message = "Forbidden"
    elif status == 400:
        message = "Bad Request"
    elif status == 404:
        message = "Not Found"
    context = {
        "message": message,
        "status_code": status,
    }
    return context
#############################################################################


def encrypt(password, salt):
    """Encrypt password."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string
#############################################################################


def invalid_credential(username, password):
    """Check invalid credential, 1 invalid 0 valid."""
    if len(username) == 0 or len(password) == 0:
        return 1
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT users.password "
        "FROM users "
        "WHERE users.username = ?",
        (username, )
    )
    identity = cur.fetchall()[0]['password']
    if len(identity) == 0:
        return 1
    salt = identity.split("$")[1]
    password_db_string = encrypt(password, salt)
    cur = connection.execute(
        "SELECT users.fullname "
        "FROM users "
        "WHERE users.username = ? AND users.password = ?",
        (username, password_db_string)
    )
    authenticate = cur.fetchall()[0]['fullname']
    if len(authenticate) == 0:
        return 1
    # credential matches
    return 0
#############################################################################


def post_outbound(postid):
    """Check postid validity, true out of bound false valid."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT max(postid) as max_id "
        "FROM posts")
    max_id = cur.fetchall()[0]['max_id']
    return int(max_id) < int(postid) or int(postid) <= 0
################################################################


def like_outbound(likeid):
    """Check likeid validity, true out of bound false valid."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT max(likeid) as MAX_ID "
        "FROM likes")
    maxid = cur.fetchall()[0]['MAX_ID']
    return int(maxid) < int(likeid) or int(likeid) <= 0
################################################################


def authentication():
    """Combine initial authentication check."""
    if flask.request.authorization is None:
        # both authentication failed
        if 'username' not in flask.session:
            return flask.jsonify(**report_status(403)), 403
        # does nothing if session is already signed in
        username = flask.session['username']
    # http access authentication on
    else:
        if 'username' not in flask.session:
            username = flask.request.authorization['username']
            password = flask.request.authorization['password']
            # check password
            if invalid_credential(username, password):
                return flask.jsonify(**report_status(403)), 403
    return username
