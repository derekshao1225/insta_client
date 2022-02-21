"""REST API for posts."""
import flask
import insta485
from insta485.api.error import post_outbound, report_status
from insta485.api.error import authentication


@insta485.app.route('/api/v1/',  methods=["GET"])
def show_resource():
    """Render API resource URLs."""
    resource = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**resource)
##########################################


@insta485.app.route('/api/v1/posts/',  methods=["GET"])
def show_api_post():
    """Return posts (size,page, postid_lte)."""
    logname = authentication()
    if isinstance(logname, tuple):
        return logname
    # size undefined default 10: return size newest post urls and ids
    size = flask.request.args.get("size", default=10, type=int)
    # page undefined default 0: return N'th page of post urls and ids
    page = flask.request.args.get("page", default=0, type=int)
    # postid_lte undefined default max
    # get max_postid
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT max(postid) as max FROM posts ")
    max_id = cur.fetchall()[0]['max']
    postid_lte = flask.request.args.get("postid_lte", default=max_id, type=int)
    # size page must be >=0
    if size < 0 or page < 0:
        return flask.jsonify(**report_status(400)), 400
    if ('size' not in flask.request.args and 'page' not in flask.request.args
            and 'postid_lte' not in flask.request.args):
        url = flask.request.path
    else:
        url = flask.request.full_path
    # contains posts shared by logname and people logname follows
    cur = connection.execute(
        "SELECT postid "
        "FROM posts "
        "WHERE postid <= ? AND owner = ? "
        "OR postid <= ? AND owner in "
        "(SELECT username2 FROM following WHERE username1 = ?) "
        "ORDER BY postid DESC LIMIT ? OFFSET ?",
        (postid_lte, logname, postid_lte, logname, size, size * page))
    posts = cur.fetchall()
    results = []
    for post in posts:
        single_p = {"postid": post['postid'],
                    "url": "/api/v1/posts/" +
                    str(post['postid']) + "/"}
        results.append(single_p)
    # figure out next url
    cur = connection.execute(
        "SELECT COUNT(*) AS countmypost "
        "FROM posts "
        "WHERE postid <=? AND owner =?",
        (postid_lte, logname))
    count = cur.fetchall()[0]['countmypost']
    cur = connection.execute(
        "SELECT COUNT(*) AS countfollowingpost "
        "FROM posts "
        "WHERE postid <=? AND owner IN "
        "(SELECT username2 FROM following WHERE username1 = ?) ",
        (postid_lte, logname))
    count += cur.fetchall()[0]['countfollowingpost']
    if count >= size * (page + 1):
        next_url = flask.request.path + "?size=" + \
            str(size) + "&page=" + str(page+1) + \
            "&postid_lte=" + str(postid_lte)
    else:
        next_url = ""
    context = {"next": next_url,
               "results": results,
               "url": url}
    return flask.jsonify(**context)
#############################################################################


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=["GET"])
def form_post(postid_url_slug):
    """Form post object."""
    logname = authentication()
    if isinstance(logname, tuple):
        return logname
    # check post bound
    if post_outbound(postid_url_slug):
        return flask.jsonify(**report_status(404)), 404
    connection = insta485.model.get_db()
    cur = connection.execute("SELECT filename, owner, created "
                             "FROM posts "
                             "WHERE postid= ? ",
                             (postid_url_slug, ))
    post = cur.fetchall()[0]
    cur = connection.execute("SELECT * "
                             "FROM users "
                             "WHERE username=? ",
                             (post['owner'], ))
    user = cur.fetchall()[0]
    cur = connection.execute("SELECT * "
                             "FROM comments "
                             "WHERE postid=? ",
                             (postid_url_slug, ))
    comments = cur.fetchall()
    cur = connection.execute(
        "SELECT COUNT(*) AS numlike "
        "FROM likes "
        "WHERE likes.owner=? AND likes.postid=?",
        (logname, postid_url_slug))
    user_like = cur.fetchall()[0]['numlike']
    if user_like == 0:
        user_like = False
        like_url = None
    else:
        user_like = True
        cur = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE likes.owner=? AND likes.postid=?",
            (logname, postid_url_slug))
        l_url = cur.fetchall()[0]['likeid']
        like_url = "/api/v1/likes/" + str(l_url) + "/"
    cur = connection.execute(
        "SELECT COUNT(*) AS numlike "
        "FROM likes "
        "WHERE likes.postid=?",
        (postid_url_slug, ))
    context = {}
    comments_info = []
    # ownership = False
    for comment in comments:
        # ownership = bool(comment['owner'] == logname)
        temp_comment = {
            "commentid": comment['commentid'],
            "lognameOwnsThis": bool(comment['owner'] == logname),
            "owner": comment['owner'],
            "ownerShowUrl": "/users/" + comment['owner'] + "/",
            "text": comment['text'],
            "url": "/api/v1/comments/" + str(comment['commentid']) + "/"
        }
        comments_info.append(temp_comment)
    likes_info = {"lognameLikesThis": user_like,
                  "numLikes": cur.fetchall()[0]['numlike'],
                  "url": like_url}
    context = {"comments": comments_info,
               "created": post["created"],
               "imgUrl": "/uploads/" + str(post['filename']),
               "likes": likes_info,
               "owner": post['owner'],
               "ownerImgUrl": "/uploads/" + str(user['filename']),
               "ownerShowUrl": "/users/" + str(user['username']) + "/",
               "postShowUrl": "/posts/" + str(postid_url_slug) + "/",
               "postid": postid_url_slug,
               "url": "/api/v1/posts/" + str(postid_url_slug) + "/"}
    return context


def get_post(postid_url_slug):
    """Return post on postid."""
    context = form_post(postid_url_slug)
    return flask.jsonify(**context)
