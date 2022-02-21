"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.index import show_img

from insta485.views.accounts import login
from insta485.views.accounts import create
from insta485.views.accounts import delete
from insta485.views.accounts import edit
from insta485.views.accounts import show_password
from insta485.views.accounts import logout


from insta485.views.users import show_user_get
from insta485.views.users import show_user_post

from insta485.views.followers import show_followers

from insta485.views.explore import explore

from insta485.views.following import show_following

from insta485.views.posts import show_post
from insta485.views.posts import posts_create_delete
from insta485.views.posts import delete_post_comments

from insta485.views.likes import likes

from insta485.views.comments import show_comments
