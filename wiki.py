import os
from flask import Flask, render_template, session, redirect, url_for, flash, Markup
from flask.ext.script import Manager, Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from py2neo import authenticate, Graph
from datetime import timedelta
from flask import session, app

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

neo4j_user = os.environ.get('NEO4J_USER') or 'neo4j'
neo4j_pass = os.environ.get('NEO4J_PASS') or ''
authenticate("localhost:7474", neo4j_user, neo4j_pass)
graph = Graph()

def get_neighbors(graph, name = None, n_neighbours = 20):
    if name is None:
        results = graph.cypher.execute("MATCH (p:Article)-[:TO_ARTICLE]->(q:Article) RETURN q.name as name LIMIT %d" % n_neighbours) 
    else:
        results = graph.cypher.execute("MATCH (p:Article{name:'%s'})-[:TO_ARTICLE]->(q:Article) RETURN q.name as name LIMIT %d" % (name, n_neighbours))
    return results

def get_path(name1, name2, depth = 5):
    return

class NameForm(Form):
    name = StringField('Root page (e.g. Hidden_Markov_model)?', validators=[Required()])
    submit = SubmitField('Submit')

#@app.before_request
#def make_session_permanent():
#    session.permanent = True
#    app.permanent_session_lifetime = timedelta(seconds = 10)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/neighbors', methods=['GET', 'POST'])
def neighbors():
    form = NameForm()
    nodes = get_neighbors(graph)
    if form.validate_on_submit():
        name = form.name.data
        neighbors = get_neighbors(graph, name).records
        if len(neighbors) == 0:
            flash(Markup('Root node not found!'))
            return redirect(url_for('neighbors'))
        else:
            session['root'] = name
            session['neighbors'] = [neighbor.name for neighbor in neighbors]
            return redirect(url_for('neighbors_result'))
    return render_template('neighbors.html', form = form)

@app.route('/neighbors_result')
def neighbors_result():
    root = session.get('root')
    neighbors = session.get('neighbors')
    return render_template('neighbors_result.html', root = root, neighbors = neighbors)

if __name__ == '__main__':
    manager.run()
