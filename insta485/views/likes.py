
"""
Insta485 likes view.

URLs include:
/likes/?target=URL
"""

import flask
import insta485


def like(logname, postid):
    """Doc."""
    # Connect to database

    connection = insta485.model.get_db()
    # operation
    connection.execute(
        "INSERT INTO likes(owner, postid) VALUES(?,?)",
        (logname, postid)
    )


def unlike(logname, postid):
    """Doc."""
    connection = insta485.model.get_db()
    connection.execute(
        "DELETE FROM likes "
        "WHERE likes.owner = ? AND likes.postid = ? ",
        (logname, postid)
    )


@insta485.app.route('/likes/', methods=['POST'])
def likes():
    """Resolve like operations."""
    logname = flask.session['username']
    postid = flask.request.form['postid']
    operation = flask.request.form['operation']
    # Connect to database
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT COUNT(*) AS numlike "
        "FROM likes "
        "WHERE likes.owner=? AND likes.postid=?",
        (logname, postid)
    )
    numlike = cur.fetchall()[0]['numlike']
    if operation == "like":
        if numlike != 0:
            flask.abort(409, 'cannot like multiple times')
        like(logname, postid)
    else:
        if numlike == 0:
            flask.abort(409, 'cannot unlike multiple times')
        unlike(logname, postid)
    # redirect to URL
    if flask.request.args['target'] is None:
        return flask.redirect(flask.url_for('show_index'))

    return flask.redirect(flask.request.args['target'])
