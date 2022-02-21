"""
Insta485 accounts view.

URLs include:
/accounts/?target=URL Immediate redirect.
/accounts/login/ ----done
/accounts/logout/ Immediate redirect.---done
/accounts/create/ --done but cannot run
/accounts/delete/
/accounts/edit/
/accounts/password/
"""
import uuid
import hashlib
import os
import pathlib
import flask
import insta485


@insta485.app.route("/accounts/login/", methods=['GET'])
def login():
    """Login GET."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    if flask.request.form.get('operation') == 'login':
        login_post()
    context = {"logname": flask.session.get('username')}
    return flask.render_template("login.html", **context)


def login_post():
    """Login POST."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    input_username = str(flask.request.form.get('username'))
    input_password = str(flask.request.form.get('password'))

    if len(input_username) == 0 or len(input_password) == 0:
        flask.abort(400)

    connection = insta485.model.get_db()
    cursor = connection.execute(
        "SELECT password FROM users WHERE username = ?", (input_username,))
    passwords = cursor.fetchall()

    pas_list = []
    for pass_word in passwords:
        pas_list.append(str(pass_word))
    if len(pas_list) == 0:
        flask.abort(403)

    true_password = passwords[0]['password']
    salt = true_password.split('$')[1]
    algorithm = true_password.split('$')[0]
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + input_password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    cursor = connection.execute(
        "SELECT COUNT(*) AS USER_COUNT FROM "
        "users WHERE username = ? AND password = ?",
        (input_username, password_db_string))
    user_count = cursor.fetchall()[0]['USER_COUNT']

    if user_count != 1:
        flask.abort(403)

    flask.session['username'] = input_username

    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Logout."""
    if 'username' in flask.session:
        flask.session.clear()
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/create/', methods=['GET'])
def create():
    """Create."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('/accounts/edit/'))
    return flask.render_template("create.html")


def create_post():
    """Create."""
    input_username = flask.request.form.get('username')
    input_password = flask.request.form.get('password')
    input_fullname = flask.request.form.get('fullname')
    input_email = flask.request.form.get('email')

    fileobj = flask.request.files["file"]
    filename = fileobj.filename
    if (not input_username or not input_password
        or not input_fullname or not input_email
            or not fileobj):
        flask.abort(400)
    if len(filename) == 0:
        flask.abort(400)
    connection = insta485.model.get_db()

    cursor = connection.execute(
        "SELECT COUNT(*) AS COUNT_EXIST "
        "FROM users WHERE username =?",
        (input_username,))
    if_exist = cursor.fetchall()[0]['COUNT_EXIST']
    if if_exist != 0:
        flask.abort(409)

    uuid_basename = set_filename()

    salt = uuid.uuid4().hex
    password_db_string = encrypt(input_password, salt)

    connection.execute("INSERT INTO users "
                       "(username, password, email,fullname,filename) "
                       "VALUES(?,?,?,?,?)",
                       (input_username, password_db_string,
                        input_email, input_fullname,
                        uuid_basename))
    flask.session['username'] = input_username

    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    return flask.redirect(flask.url_for('show_index'))


@insta485.app.route('/accounts/delete/', methods=['GET'])
def delete():
    """Delete."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session['username']
    context = {'logname': logname}
    return flask.render_template("delete.html", **context)


def delete_post():
    """Doc."""
    if 'username' not in flask.session:
        return flask.abort(403, 'No deletion when signed out')
    logname = flask.session['username']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT users.filename "
        "FROM users "
        "WHERE users.username = ?",
        (logname, )
    )
    user_profile = cur.fetchall()[0]['filename']
    path = insta485.app.config["UPLOAD_FOLDER"]/user_profile
    os.remove(path)
    cur = connection.execute(
        "SELECT posts.filename "
        "FROM posts "
        "WHERE posts.owner = ? ",
        (logname, )
    )
    user_file = cur.fetchall()
    for file in user_file:
        path = insta485.app.config["UPLOAD_FOLDER"]/file['filename']
        os.remove(path)
    connection.execute(
        "DELETE FROM users WHERE username = ?",
        (logname, )
    )
    flask.session.clear()
    return flask.redirect(flask.url_for('create'))


@insta485.app.route('/accounts/edit/', methods=['GET'])
def edit():
    """Edit."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    logname = flask.session['username']
    cursor_ = connection.execute(
        "SELECT * FROM users WHERE users.username = ?", (logname,))
    current = cursor_.fetchall()[0]
    context = {'logname': current['username'],
               'fullname': current['fullname'],
               'email': current['email'],
               "filename": current['filename']
               }
    return flask.render_template("edit.html", **context)


def edit_post():
    """Edit operation."""
    if 'username' not in flask.session:
        flask.abort(403)

    connection = insta485.model.get_db()
    logname = flask.session.get('username')
    input_fullname = flask.request.form.get('fullname')
    input_email = flask.request.form.get('email')

    fileobj = flask.request.files["file"]
    filename = fileobj.filename

    # if filename != '':
    #     uuid_basename = "{stem}{suffix}".format(
    #         stem=uuid.uuid4().hex,
    #         suffix=pathlib.Path(filename).suffix
    #     )

    #     # Save to disk
    #     path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    #     fileobj.save(path)
    uuid_basename = set_filename()

    if len(input_fullname) == 0 or len(input_email) == 0:
        flask.abort(400)

    connection = insta485.model.get_db()
    connection.execute("UPDATE users SET fullname = ?, email = ? "
                       "WHERE users.username = ?",
                       (input_fullname, input_email, logname))
    if filename != '':
        connection.execute(
            "UPDATE users SET filename = ? "
            "WHERE users.username = ?",
            (uuid_basename, logname))


@insta485.app.route('/accounts/password/')
def show_password():
    """Edit/view password information."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('password.html')


def encrypt(input_password, salt):
    """Efc."""
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + input_password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def set_filename():
    """Def."""
    # Unpack flask object
    fileobj = flask.request.files["file"]
    if fileobj is None:
        flask.abort(400, 'empty file')
    filename = fileobj.filename

    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f"{stem}{suffix}"
    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename


def op_update():
    """Oc."""
    if 'username' not in flask.session:
        return flask.abort(403, 'No active session')
    logname = flask.session['username']
    password = flask.request.form['password']
    new_password1 = flask.request.form['new_password1']
    new_password2 = flask.request.form['new_password2']
    if password is None or \
        new_password1 is None or\
            new_password2 is None:
        flask.abort(400, 'Missing fields')
    if new_password1 != new_password2:
        flask.abort(401, 'Passwords do not match')
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (logname, )
    )
    authentication = cur.fetchall()[0]['password']
    split = authentication.split("$")
    salt = split[1]
    password = encrypt(password, salt)
    if password != authentication:
        flask.abort(403, 'Password authentication failed')
    else:
        salt = uuid.uuid4().hex
        new_password = encrypt(new_password1, salt)
        connection.execute("UPDATE users SET password = ? WHERE username = ?",
                           (new_password, logname)
                           )
    if flask.request.args['target'] is None:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])


@insta485.app.route('/accounts/', methods=['POST'])
def all_post():
    """All the post operations."""
    if flask.request.form.get('operation') == 'login':
        login_post()

    if flask.request.form.get('operation') == 'create':
        create_post()

    if flask.request.form.get('operation') == 'delete':
        delete_post()

    if flask.request.form.get('operation') == 'edit_account':
        edit_post()

    if flask.request.form.get('operation') == 'update_password':
        op_update()

    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    return flask.redirect(flask.url_for('show_index'))
