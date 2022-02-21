"""
Insta485 users view.

URLs include:
/users/<user_url_slug>/
/users/<user_url_slug>/followers
/users/<user_url_slug>/following/
"""

import flask
import insta485
from insta485.views.accounts import set_filename


@insta485.app.route('/users/<username>/', methods=['GET'])
def show_user_get(username):
    """Show the user."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    # logname here is username in html
    logname = flask.session.get('username')
    connection = insta485.model.get_db()

    cursor = connection.execute("SELECT * FROM users")
    all_users = cursor.fetchall()

    # print(all_users)
    all_user_list = []
    for user in all_users:
        all_user_list.append(user['username'])

    if username not in all_user_list:
        flask.abort(404)

    cursor = connection.execute(
        "SELECT COUNT(*) AS POST_COUNT FROM posts WHERE owner=?", (username,))
    post_count = cursor.fetchall()[0]['POST_COUNT']

    cursor = connection.execute(
        "SELECT COUNT(*) AS FOLLOWING_COUNT FROM following "
        "WHERE username1 = ?", (username,))
    following_count = cursor.fetchall()[0]['FOLLOWING_COUNT']

    cursor = connection.execute(
        "SELECT COUNT(*) AS FOLLOWER_COUNT FROM following "
        "WHERE username2 = ?", (username,))
    follower_count = cursor.fetchall()[0]['FOLLOWER_COUNT']

    cursor = connection.execute(
        "SELECT * from posts where owner = ?", (username,))
    posts = cursor.fetchall()

    cursor = connection.execute(
        "SELECT * FROM users WHERE username = ?", (username,))
    users = cursor.fetchall()
    fullname = users[0]['fullname']

    # print(posts)

    isfollowing = False

    cursor = connection.execute(
        "SELECT COUNT(*) AS COUNT_FL FROM "
        "following WHERE username1 = ? AND username2 = ?",
        (logname, username))
    if cursor.fetchall()[0]['COUNT_FL'] == 1:
        isfollowing = True

    context = {'logname': logname,
               'total_posts': post_count,
               'username': username, "fullname": fullname,
               "followers": follower_count,
               "following": following_count, "posts": posts,
               'isfollowing': isfollowing}
    return flask.render_template("user.html", **context)


@insta485.app.route('/users/<username>/', methods=['POST'])
def show_user_post(username):
    """Dc."""
    # if 'username' not in username:
    #     return flask.redirect(flask.url_for('login_get'))

    if flask.request.form.get('operation') == 'create_post':
        # Unpack flask object
        uuid_basename = set_filename()
        connection = insta485.model.get_db()
        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES (?, ?)",
            (uuid_basename, username))

    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))
    return flask.redirect(flask.url_for('show_user_get'))
