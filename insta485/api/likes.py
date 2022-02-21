"""
REST API for likes.

Handles POST DELETE like
"""

import flask
import insta485
from insta485.api.error import report_status, authentication
from insta485.api.error import like_outbound


@insta485.app.route('/api/v1/likes/<likeid>/', methods=["DELETE"])
def delete_like(likeid):
    """Delete like based on the comment id."""
    logname = authentication()
    if isinstance(logname, tuple):
        return logname
    connection = insta485.model.get_db()
    # 404 if likeid doesn't exist
    if like_outbound(likeid):
        return flask.jsonify(**report_status(404)), 404
    cur = connection.execute("SELECT owner "
                             "FROM likes "
                             "WHERE likeid=? ",
                             (likeid, ))
    like_owner = cur.fetchall()[0]['owner']
    # 403 if user doesn't own the like
    if like_owner != logname:
        return flask.jsonify(**report_status(403)), 403
    connection.execute("DELETE FROM likes "
                       "WHERE likeid = ? ",
                       (likeid, ))
    context = {}
    return flask.jsonify(**context), 204
#############################################################################


@insta485.app.route('/api/v1/likes/', methods=["POST"])
def post_like():
    """Create a new like for specified post id."""
    logname = authentication()
    if isinstance(logname, tuple):
        return logname
    postid = flask.request.args.get('postid')
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT COUNT(*) AS numlike "
                             "FROM likes "
                             "WHERE owner=? AND postid=? ",
                             (logname, postid))
    # None: no like created; A number if already exists
    like_id = cur.fetchall()[0]['numlike']
    status = 200
    if like_id == 0:
        cur = connection.execute(
            "INSERT INTO likes(owner, postid) VALUES(?,?)",
            (logname, postid))
        like_id = cur.lastrowid
        status = 201
    else:
        cur = connection.execute("SELECT likeid "
                                 "FROM likes "
                                 "WHERE owner=? AND postid=? ",
                                 (logname, postid))
        like_id = cur.fetchall()[0]['likeid']
    context = {"likeid": like_id,
               "url": "/api/v1/likes/" + str(like_id) + "/"}
    return flask.jsonify(**context), status
