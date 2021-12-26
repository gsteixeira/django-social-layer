DJANGO SOCIAL LAYER
---------------------

django-social-layer - Adds social media features to any website.

FEATURES
-----------
    - easly add a comment section to any webpage
    - users can like comments
    - notifications
    - users have profile page
    - New: users now can post content, images, videos, etc.


INSTALATION
-----------

Install django-social-layer:

.. code:: shell

       pip install django-social-layer

Add to urls.py:

.. code:: python

        path('', include(('social_layer.urls', 'social_layer'), namespace="social_layer"))

add to settings.py:

.. code:: python

       INSTALLED_APPS = [
           # ...
           'social_layer.apps.SocialLayerConfig',
           'infscroll', # required
       ]

       # the login url to redirect site visitors to a social account.
       # Note that you need to take care of auth and user registration.
       SOCIAL_VISITOR_LOGIN = '/login/'

run migrations:

.. code:: shell

       ./manage.py migrate


USAGE
-----

Create a CommentSection for any purpose. It can, for example, be linked to an \
object with a ForeignKey field, or to a view by it's URL. In our example we will \
use an url, but it's optional. A CommentSection optionally can have an owner.

.. code:: python

    from social_layer.comments.models import CommentSection
    comment_section = CommentSection.objects.create(url=request.path)

Now inside a view, lets add a commennt section for the page:

.. code:: python

    from social_layer.comments.models import CommentSection
    def my_view(request):
        # in this example, we'll use the url to match the page.
        cmt_section, n  = CommentSection.objects.get_or_create(url=request.path)
        return render(request, 'my_view.html',
                      {'comment_section': cmt_section})

To finish, add this to the template:

.. code:: html

    {% load static %}
    <script defer application="javascript" src="{% static 'social_layer/js/social_layer.js' %}"></script>
    <link rel="stylesheet" href="{% static 'social_layer/css/social_layer.css' %}"/>
    ...
    <p>The comment section will render below.</p>
    {% include 'social_layer/comments/comment_section.html' %}



Get and create a SocialProfile for an authenticated user:

.. code:: python

    from social_layer.utils import get_social_profile
    def my_view(request):
        profile = get_social_profile(request)


Hope this can be useful to you.
