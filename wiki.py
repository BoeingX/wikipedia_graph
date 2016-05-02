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
import re

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

neo4j_user = os.environ.get('NEO4J_USER') or 'neo4j'
neo4j_pass = os.environ.get('NEO4J_PASS') or 'neo4j'
authenticate("localhost:7474", neo4j_user, neo4j_pass)
graph = Graph()

def get_neighbors(graph, name = None, n_neighbours = 20):
    if name is None:
        results = graph.cypher.execute("MATCH (p:Article)-[:TO_ARTICLE]->(q:Article) RETURN p.name as root, q.name as name LIMIT %d" % n_neighbours) 
    else:
        results = graph.cypher.execute("MATCH (p:Article)-[:TO_ARTICLE]->(q:Article) WHERE p.name =~ '(?i)%s' RETURN p.name as root, q.name as name LIMIT %d" % (name, n_neighbours))
    return results

def get_path(graph, name1, name2, depth = 5):
    result = graph.cypher.execute("MATCH s = shortestPath((p:Article)-[:TO_ARTICLE*1..%d]->(q:Article)) WHERE p.name =~ '(?i)%s' and q.name =~ '(?i)%s' RETURN s as path LIMIT 1" % (depth, name1, name2))
    return result

class NameForm(Form):
    name = StringField('Root page (e.g. Hidden Markov model)?', validators=[Required()])
    submit = SubmitField('Submit')

class PathForm(Form):
    name1 = StringField('First page (e.g. Hidden Markov model)?', validators=[Required()])
    name2 = StringField('First page (e.g. Support vector machine)?', validators=[Required()])
    submit = SubmitField('Submit')

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
        name = re.sub(' ', '_', form.name.data)
        neighbors = get_neighbors(graph, name).records
        if len(neighbors) == 0:
            flash(Markup('Root node not found!'))
            return redirect(url_for('neighbors'))
        else:
            session['root'] = neighbors[0].root
            session['neighbors'] = [neighbor.name for neighbor in neighbors]
            return redirect(url_for('neighbors_result'))
    return render_template('neighbors.html', form = form)

@app.route('/neighbors_result')
def neighbors_result():
    root = session.get('root')
    neighbors = session.get('neighbors')
    if root is None or neighbors is None:
        return render_template('404.html'), 404
    return render_template('neighbors_result.html', root = root, neighbors = neighbors)

@app.route('/path', methods=['GET', 'POST'])
def path():
    form = PathForm()
    if form.validate_on_submit():
        name1 = re.sub(' ', '_', form.name1.data)
        name2 = re.sub(' ', '_', form.name2.data)
        path = get_path(graph, name1, name2).records
        if len(path) == 0:
            flash(Markup('Path not found!'))
            return render_template('neighbors.html', form = form)
        else:
            path = [node['name'] for node in path[0].path.nodes]
            print path
            return redirect(url_for('index'))
    return render_template('neighbors.html', form = form)


if __name__ == '__main__':
    manager.run()
