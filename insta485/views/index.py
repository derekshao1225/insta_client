"""

Insta485 index (main) view.

URLs include:
/
"""

import flask
import arrow
import insta485


@insta485.app.route("/uploads/<path:name>")
def show_img(name):
    """Show_Img."""
    if not flask.session.get('username'):
        flask.abort(403)
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], name, as_attachment=True
    )


@insta485.app.route('/')
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()
    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))

    context = {}
    logname = flask.session.get('username')
    cursor_posts = connection.execute(
        "SELECT * FROM posts ORDER BY postid DESC")
    posts = cursor_posts.fetchall()

    # cursor_users = connection.execute("SELECT * FROM users")
    # users = cursor_users.fetchall()

    # print(all_users)

    cursor_followings = connection.execute(
        "SELECT username2 FROM following WHERE username1 = ?", (logname,))
    post_user_list = []
    post_user_list.append(logname)
    followings = cursor_followings.fetchall()
    for following in followings:
        post_user_list.append(following['username2'])

    # for user in users:
    #     if str(user['username']) not in post_user_list:
    #         idx = users.index(user)
    #         users.pop(idx)

    context['posts'] = index_helper(posts, post_user_list)

    # context['users'] = users
    context['logname'] = logname
    return flask.render_template("index.html", **context)


def index_helper(posts, post_user_list):
    """DC."""
    connection = insta485.model.get_db()
    result_list = []
    for post in posts:
        if post['owner'] in post_user_list:
            cursor_comments = connection.execute(
                "SELECT owner, text, commentid "
                "FROM comments "
                "WHERE postid = ?"
                "ORDER BY commentid", (post['postid'], ))
            post['comments'] = cursor_comments.fetchall()
            cursor_likes = connection.execute(
                "SELECT COUNT(*) AS num "
                "FROM likes "
                "WHERE postid = ?", (post['postid'], ))
            cursor_user = connection.execute(
                "SELECT filename "
                "FROM users "
                "WHERE username = ?", (post['owner'], ))
            post['likes'] = cursor_likes.fetchone()['num']  # potenial bug
            post['img_url'] = post['filename']
            post['user_img_url'] = cursor_user.fetchone()['filename']
            post['created'] = arrow.get(post['created']).humanize()
            result_list.append(post)
    return result_list
