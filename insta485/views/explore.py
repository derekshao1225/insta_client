"""
Insta485 explore view.

URLs include:
/explore/ --done
"""
import flask
import insta485


@insta485.app.route('/explore/', methods=['GET', 'POST'])
def explore():
    """Show explore."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()

    logname = flask.session.get('username')

    cursor = connection.execute(
        "SELECT username FROM users WHERE username != ?", (logname,))
    all_other_users = cursor.fetchall()

    all_other_users_list = []
    for other_user in all_other_users:
        all_other_users_list.append(str(other_user['username']))

    cursor = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?", (logname,))
    all_follows = cursor.fetchall()

    all_follows_list = []
    for follow in all_follows:
        all_follows_list.append(str(follow['username2']))

    all_unfollows_list = []
    for user in all_other_users_list:
        if user not in all_follows_list:
            all_unfollows_list.append(str(user))

    not_following = []
    for user in all_unfollows_list:
        cursor = connection.execute(
            "SELECT filename from users WHERE username = ?", (user,))
        user_img_url = cursor.fetchall()[0]['filename']
        temp_dict = {}
        temp_dict['username'] = user
        temp_dict['user_img_url'] = user_img_url
        not_following.append(temp_dict)

    context = {'logname': logname, 'not_following': not_following}
    return flask.render_template('explore.html', **context)


# @insta485.app.route('/explore/')
# def explore():
#     """Display explore page."""
#     if 'username' not in flask.session:
#         return flask.redirect(flask.url_for('login'))
#     # Connect to database
#     connection = insta485.model.get_db()
#     logname = flask.session['username']
#     # Query database
#     cur = connection.execute(
#         "SELECT username, filename FROM users "
#         "WHERE username != ? AND "
#         "username NOT IN "
#         "(SELECT username2 FROM following WHERE username1=?)",
#         (logname, logname)
#     )
#     need_follow = cur.fetchall()
#     context = {"not_following": need_follow}
#     return flask.render_template("explore.html", **context)

# @insta485.app.route('/explore/')
# def explore():
#     """Display explore page """
#     if 'username' not in flask.session:
#         return flask.redirect(flask.url_for('login'))
#     # Connect to database
#     connection = insta485.model.get_db()
#     logname = flask.session['username']
#     # Query database
#     cur = connection.execute(
#         "SELECT users.username, users.filename  "
#         "FROM users "
#         "WHERE users.username != ? AND users.username NOT IN "
#         "(SELECT following.username2 "
#         "FROM following "
#         "WHERE following.username1=?)",
#         (logname, logname)
#     )
#     not_following = cur.fetchall()
#     context = {"not_following": not_following}
#     return flask.render_template("explore.html", **context)
