"""
Insta485 posts view.

URLs include:
/posts/<postid_url_slug>/
/posts/?target=URL
"""
import os
import arrow
import flask
import insta485
from insta485.views.accounts import set_filename


@insta485.app.route('/posts/<postid>/', methods=['GET', 'POST'])
def show_post(postid):
    """Display /posts/postid/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    logname = flask.session.get('username')
    connection = insta485.model.get_db()

    cursor = connection.execute(
        "SELECT * FROM posts WHERE postid = ?", (postid,))
    posts = cursor.fetchall()
    if len(posts) == 0:
        flask.abort(403)
    post = posts[0]
    owner = post['owner']
    img_url = post['filename']
    time = post['created']
    time = arrow.get(time).humanize()

    cursor = connection.execute(
        "SELECT * FROM users WHERE username = ?", (owner,))
    owner_img_url = cursor.fetchall()[0]['filename']

    cursor = connection.execute(
        "SELECT COUNT(*) AS COUNT_LIKES FROM "
        "likes WHERE owner = ? and postid = ?", (logname, postid))
    num_like_or_not = cursor.fetchall()[0]['COUNT_LIKES']
    like_or_not = False
    if num_like_or_not == 1:
        like_or_not = True

    cursor = connection.execute(
        "SELECT * FROM comments WHERE postid = ?", (postid,))
    comments = cursor.fetchall()

    cursor = connection.execute(
        "SELECT COUNT(*) as LIKES FROM likes WHERE postid = ?", (postid,))
    likes = cursor.fetchall()[0]['LIKES']

    context = {"logname": logname,
               "postid": postid, "owner": owner,
               "owner_img_url": owner_img_url,
               "img_url": img_url,
               "timestamp": time,
               "likes": likes,
               "comments": comments,
               "post_like_or_not": like_or_not}

    return flask.render_template('post.html', **context)


@insta485.app.route('/posts/', methods=['POST'])
def posts_create_delete():
    """Post create/delete."""
    logname = flask.session.get('username')
    if flask.request.form.get('operation') == 'create':
        # fileobj = flask.request.files["file"]
        # if fileobj is None:
        #     flask.abort(400)
        # filename = fileobj.filename
        # uuid_basename = "{stem}{suffix}".format(
        #     stem=uuid.uuid4().hex,
        #     suffix=pathlib.Path(filename).suffix
        # )
        # path_ = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        # fileobj.save(path_)
        uuid_basename = set_filename()
        connection = insta485.model.get_db()
        connection.execute(
            "INSERT INTO posts (filename, owner) "
            "VALUES (?, ?)", (uuid_basename, logname))
        if 'target' in flask.request.args:
            return flask.redirect(flask.request.args.get('target'))
        path = '/users/' + logname + '/'
    elif flask.request.form.get('operation') == 'delete':
        postid = flask.request.form.get('postid')
        logname = flask.session.get('username')
        connection = insta485.model.get_db()
        cursor_posts = connection.execute(
            "SELECT * FROM posts WHERE postid = ?", (postid,))
        posts = cursor_posts.fetchall()
        owner = posts[0]['owner']
        if owner != logname:
            flask.abort(403)
        file_path = insta485.app.config['UPLOAD_FOLDER'] / posts[0]['filename']
        os.remove(file_path)
        # file_handle.close()
        connection.execute("DELETE FROM posts WHERE postid = ?", (postid,))
        path = '/users/' + logname + '/'
    return flask.redirect(path)


@insta485.app.route('/posts/', methods=['POST'])
def delete_post_comments():
    """Delete Posts' comments."""
    connection = insta485.model.get_db()
    comment_id = flask.request.form.get('commentid')
    connection.execute(
        "DELETE FROM comments WHERE commentid = ?", (comment_id,))
    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get("target"))
    return flask.redirect(flask.url_for('show_index'))
