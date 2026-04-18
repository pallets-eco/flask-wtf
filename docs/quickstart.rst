Quickstart
==========

Eager to get started? This page gives a good introduction to Flask-WTF.
It assumes you already have Flask-WTF installed. If you do not, head over
to the :doc:`install` section.


Creating Forms
--------------

Flask-WTF provides your Flask application integration with WTForms. For example::

    from flask_wtf import FlaskForm
    from wtforms import StringField
    from wtforms.validators import DataRequired

    class MyForm(FlaskForm):
        name = StringField('name', validators=[DataRequired()])


.. note::

   From version 0.9.0, Flask-WTF will not import anything from wtforms,
   you need to import fields from wtforms.

In addition, a CSRF token hidden field is created automatically. You can
render this in your template:

.. sourcecode:: html+jinja

    <form method="POST" action="/">
        {{ form.csrf_token }}
        {{ form.name.label }} {{ form.name(size=20) }}
        <input type="submit" value="Go">
    </form>

If your form has multiple hidden fields, you can render them in one
block using :meth:`~flask_wtf.FlaskForm.hidden_tag`.

.. sourcecode:: html+jinja

    <form method="POST" action="/">
        {{ form.hidden_tag() }}
        {{ form.name.label }} {{ form.name(size=20) }}
        <input type="submit" value="Go">
    </form>


Validating Forms
----------------

Validating the request in your view handlers::

    @app.route('/submit', methods=['GET', 'POST'])
    def submit():
        form = MyForm()
        if form.validate_on_submit():
            return redirect('/success')
        return render_template('submit.html', form=form)

Note that you don't have to pass ``request.form`` to Flask-WTF; it will
load automatically. And the convenient ``validate_on_submit`` will check
if it is a POST request and if it is valid.

If your forms include validation, you'll need to add to your template to display
any error messages.  Using the ``form.name`` field from the example above, that
would look like this:

.. sourcecode:: html+jinja

    {% if form.name.errors %}
        <ul class="errors">
        {% for error in form.name.errors %}
            <li>{{ error }}</li>
        {% endfor %}
        </ul>
    {% endif %}

Heading over to :doc:`form` to learn more skills.
