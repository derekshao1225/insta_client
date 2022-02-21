"""
Insta485 followers view.

URLs include:

"""
import flask
import insta485


@insta485.app.route("/users/<username>/followers/", methods=["GET", 'POST'])
def show_followers(username):
    """Show followers."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("login"))

    connection = insta485.model.get_db()
    logname = flask.session.get('username')

    cursor = connection.execute("SELECT * FROM users")
    all_users = cursor.fetchall()

    username_list = []
    for user in all_users:
        username_list.append(user['username'])

    if username not in username_list:
        flask.abort(404)

    if flask.request.method == 'POST':
        username = flask.request.form.get('username')
        cursor = connection.execute(
            "SELECT COUNT(*) AS NUM_FOLLOWING_NOT "
            "FROM following WHERE username1 = ? "
            "AND username2 = ?", (logname, username))
        num_follow_or_not = cursor.fetchall()[
            0]['NUM_FOLLOWING_NOT']

        if flask.request.form.get('operation') == 'follow':
            if num_follow_or_not != 1:
                flask.abort(409)
            connection.execute(
                'INSERT INTO following(username1, username2) values(?,?)',
                (logname, username,))
        elif flask.request.form.get('operation') == 'unfollow':
            if num_follow_or_not == 1:
                flask.abort(409)
            connection.execute(
                'DELETE FROM following WHERE username1 = ? AND username2 = ?',
                (logname, username,))

        if 'target' in flask.request.args:
            return flask.redirect(flask.request.args.get('target'))
        return flask.redirect(flask.url_for("show_followers"))

    cursor = connection.execute(
        "SELECT * FROM users, following "
        "WHERE users.username = following.username1 "
        "AND following.username2 = ?", (username,))
    followers = cursor.fetchall()

    for follow in followers:
        follow['user_img_url'] = '/uploads/' + follow['filename']
        current_username = follow['username']
        cursor = connection.execute(
            "SELECT COUNT(*) AS CLU FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, current_username))
        logname_follows_username = cursor.fetchall()
        follow['logname_follows_username'] = logname_follows_username[0]['CLU']

    context = {'followers': followers,
               'logname': logname, 'username': username}

    return flask.render_template('followers.html', **context)
