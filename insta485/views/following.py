"""Following."""
import flask
import insta485


def follow(logname, username):
    """DOc."""
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO following "
        "(username1, username2) VALUES(?,?)",
        (logname, username)
    )


def unfollow(logname, username):
    """Doc."""
    connection = insta485.model.get_db()
    connection.execute(
        "DELETE FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (logname, username)
    )


@insta485.app.route('/following/', methods=['POST'])
def following():
    """Resolve following requests."""
    logname = flask.session['username']
    username = flask.request.form['username']
    operation = flask.request.form['operation']
    connection = insta485.model.get_db()
    connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE following.username1 = ? AND following.username2 = ?",
        (logname, username)
    )
    # relationship = cur.fetchall()
    if operation == "follow":
        # if relationship is not None:
        #     flask.abort(408, 'cannot follow again')
        follow(logname, username)
    else:
        # if relationship is None:
        #     flask.abort(409, 'cannot unfollow again')
        unfollow(logname, username)
    # redirect
    if flask.request.args['target'] is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args['target'])


@insta485.app.route('/users/<username>/following/', methods=['GET', 'POST'])
def show_following(username):
    """Show Following."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session['username']
    connection = insta485.model.get_db()

    cursor_all_users = connection.execute("SELECT * FROM users")
    all_users = cursor_all_users.fetchall()
    all_users_list = []
    for user in all_users:
        all_users_list.append(user['username'])
    if username not in all_users_list:
        flask.abort(404, 'No such a user')
    if flask.request.method == 'POST':
        following()
    cursor_all_users = connection.execute(
        "SELECT * FROM users, following WHERE "
        "following.username2 = users.username "
        "AND username1 = ?", (username,))
    all_users = cursor_all_users.fetchall()
    following_list = []
    for user in all_users:
        temp_name = user['username']
        temp_filename = user['filename']
        temp_cursor = connection.execute(
            "SELECT COUNT(*) AS COUNT_FOLLOWING "
            "FROM following WHERE username1 = ? "
            "AND username2 = ?", (logname, temp_name))
        logname_follows_username = temp_cursor.fetchall()[0]['COUNT_FOLLOWING']
        temp_dict = {}
        temp_dict['username'] = temp_name
        temp_dict['user_img_url'] = temp_filename
        temp_dict['logname_follows_username'] = logname_follows_username
        following_list.append(temp_dict)
    context = {'logname': logname, 'username': username,
               'following': following_list}
    return flask.render_template("following.html", **context)
