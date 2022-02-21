"""Insta485 comments view."""
import flask
import insta485


@insta485.app.route('/comments/', methods=["POST"])
def show_comments():
    """Display /comments/ route."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('login'))
    if flask.request.form.get('operation') == 'create':
        username = flask.session.get('username')
        postid = flask.request.form['postid']
        text = flask.request.form['text']
        if len(str(text)) <= 0:
            flask.abort(400)
        connection = insta485.model.get_db()
        connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES(?, ?, ?)", (username, postid, text))
    elif flask.request.form.get('operation') == 'delete':
        logname = flask.session.get('username')
        comment_id = flask.request.form['commentid']
        connection = insta485.model.get_db()
        cursor_comments = connection.execute(
            "SELECT * FROM comments WHERE commentid = ?", (comment_id,))
        comments = cursor_comments.fetchall()
        ownername = comments[0]['owner']
        if ownername != logname:
            flask.abort(403)
        connection.execute(
            "DELETE FROM comments WHERE commentid = ?", (comment_id,))
    if 'target' in flask.request.args:
        return flask.redirect(flask.request.args.get('target'))

    return flask.redirect(flask.url_for('show_index'))
