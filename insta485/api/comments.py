"""
REST API for posts.

Handles POST DELETE comments
"""
import flask
import insta485
from insta485.api.error import post_outbound, report_status
from insta485.api.error import authentication


@insta485.app.route('/api/v1/comments/', methods=["POST"])
def post_comment():
    """Create a new comment for specified post id."""
    logname = authentication()
    if isinstance(logname, tuple):
        return logname
    postid = int(flask.request.args.get('postid'))
    # out of bound
    if post_outbound(postid):
        context = report_status(404)
        return flask.jsonify(**context), 404
    connection = insta485.model.get_db()
    connection.execute(
        "INSERT INTO comments(owner, postid, text) VALUES(?,?,?)",
        (logname, postid, flask.request.json['text'])
    )
    cur = connection.execute(
        "SELECT last_insert_rowid() as last FROM comments ")
    last_insert = cur.fetchall()[0]['last']
    insert_id = 0
    if last_insert is not None:
        insert_id = last_insert
    # prepare new comment to be added
    new_cmt = {
        "commentid": insert_id,
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": "/users/" + str(logname) + "/",
        "text": flask.request.json['text'],
        "url": "/api/vi/comments/" + str(postid) + "/"
    }
    return flask.jsonify(**new_cmt), 201
#############################################################################


@insta485.app.route('/api/v1/comments/<commentid>/', methods=["DELETE"])
def delete_comment(commentid):
    """Delete the comment based on the comment id."""
    logname = authentication()
    if isinstance(logname, tuple):
        return logname
    connection = insta485.model.get_db()
    # 404 if commentid doesn't exist
    cur = connection.execute("SELECT COUNT(*) AS c_count "
                             "FROM comments "
                             "WHERE commentid =? ",
                             (commentid, ))
    c_count = cur.fetchall()[0]['c_count']
    if c_count == 0:
        return flask.jsonify(**report_status(404)), 404
    cur = connection.execute("SELECT owner "
                             "FROM comments "
                             "WHERE commentid =? ",
                             (commentid, ))
    comment_owner = cur.fetchall()[0]['owner']
    # 403 if user doesn't own the comment
    if comment_owner != logname:
        return flask.jsonify(**report_status(403)), 403
    connection.execute("DELETE FROM comments "
                       "WHERE commentid = ? ",
                       (commentid, ))
    context = {}
    return flask.jsonify(**context), 204
