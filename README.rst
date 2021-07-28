DJANGO SOCIAL LAYER
---------------------

django-social-layer - Adds social media features to any website.

FEATURES
-----------
    - easly add a comment section to any webpage
    - users can like comments
    - notifications
    - users have profile page


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
           ...
           'social_layer',
       ]

run migrations:

.. code:: shell

       ./manage.py migrate social_layer


USAGE
-----
Create a SocialProfile for an user:

.. code:: python

    bob = User.objects.create(username="bob")
    social_bob = SocialProfile.objects.create(user=bob)

Create a CommentSection for any purpose. It can, for example, be linked to an \
object with a ForeignKey field, or to a view by it's URL. In our example we will \
use an url, but it's optional. A CommentSection optionally can have an owner.

.. code:: python

    comment_section = CommentSection.objects.create(url=request.path)


Now inside a view, lets add a commennt section for the page:

.. code:: python

    def some_awesome_view(request):
        # in this example, we'll use the url to match the page.
        cmt_section, n  = CommentSection.objects.get_or_create(url=request.path)
        return render(request, 'awesome_template.html',
                      {'comment_section': cmt_section})

To finish, add this to the template:

.. code:: html

    {% load static %}
    <script defer application="javascript" src="{% static 'social_layer/js/social_layer.js' %}"></script>
    <link rel="stylesheet" href="{% static 'social_layer/css/social_layer.css' %}"/>
    ...
    <p>The comment section will render below.</p>
    {% include 'comments/comment_section.html' %}


Hope this can be useful to you.
