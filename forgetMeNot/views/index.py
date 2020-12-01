"""
forgetMeNot index (main) view.

URLs include:
/
"""
import flask
import forgetMeNot


@forgetMeNot.app.route('/')
def show_index():
    """Display / route."""

    # Connect to database
    connection = forgetMeNot.model.get_db()

    # Query database
    cur = connection.execute(
        "SELECT patientID, fullname "
        "FROM patients"
    )
    users = cur.fetchall()

    # Add database info to context
    context = {"users": users}
    return flask.render_template("index.html", **context)
