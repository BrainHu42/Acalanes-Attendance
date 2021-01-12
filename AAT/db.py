import psycopg2
from urllib.parse import urlparse

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            database = 'test',
            user = 'postgres',
            password = 'password',
            host = 'localhost',
        )
        # result = urlparse(current_app.config['DATABASE'])
        # username = result.username
        # password = result.password
        # database = result.path[1:]
        # hostname = result.hostname
        # g.db = psycopg2.connect(
        #     database = database,
        #     user = username,
        #     password = password,
        #     host = hostname
        # )
        g.db.cursor().execute('SET timezone = %s;', ('America/Los_Angeles',))

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.cursor().execute(f.read().decode('utf8'))
        db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)