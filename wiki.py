import os
import re
import json
import random
from flask import Flask, render_template, session, redirect, url_for, flash, Markup, jsonify, app, request
from flask.ext.script import Manager, Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from py2neo import authenticate, Graph
from datetime import timedelta
from flask_bootstrap import WebCDN

basedir = os.path.abspath(os.path.dirname(__file__))

neo4j_user = os.environ.get('NEO4J_USER') or 'neo4j'
neo4j_pass = os.environ.get('NEO4J_PASS') or 'neo4j'
authenticate("localhost:7474", neo4j_user, neo4j_pass)
graph = Graph()
cypher = graph.cypher

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.extensions['bootstrap']['cdns']['jquery'] = WebCDN('//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/')

class NameForm(Form):
    name1 = StringField('First page (e.g. Hidden Markov model)?', validators=[Required()])
    name2 = StringField('Second page (e.g. Support vector machine)?', validators = [])
    submit = SubmitField('Submit')

@app.route('/autocomplete',methods=['GET'])
def autocomplete():
    search = request.args.get('query')
    search = re.sub(' +', '_', search)
    match = cypher.execute("MATCH (p:Article) WHERE p.name =~ '(?i)%s.*' RETURN p.name as name LIMIT 5" % search).records
    match = [node.name for node in match] if len(match) > 0 else []
    return jsonify(json_list=match) 

def get_neighbors(graph, name = None, n_neighbors = 20):
    if name is None:
        results = cypher.execute("MATCH (p:Article)-[:TO_ARTICLE]->(q:Article) RETURN p, q SKIP %d LIMIT %d" % (random.randint(0, 1e6), n_neighbors)).records
    else:
        results = cypher.execute("MATCH (p:Article)-[:TO_ARTICLE]->(q:Article) WHERE p.name =~ '(?i)%s' RETURN p, q LIMIT %d" % (name, n_neighbors)).records
    if len(results) == 0:
        return None
    g = {}
    g['nodes'] = []
    g['edges'] = []
    nodes = set()
    for idx in range(len(results)):
        tmp = results[idx]
        if tmp.p['pageid'] not in nodes:
            g['nodes'].append({'id': tmp.p['pageid'], 'label': tmp.p['name'], 'x': random.random()*10, 'y': random.random()*10, 'size': 1})
            nodes.add(tmp.p['pageid'])
        if tmp.q['pageid'] not in nodes:
            g['nodes'].append({'id': tmp.q['pageid'], 'label': tmp.q['name'], 'x': random.random()*10, 'y': random.random()*10, 'size': 1})
            nodes.add(tmp.q['pageid'])
        g['edges'].append({'id': str(idx), 'source': tmp.p['pageid'], 'target': tmp.q['pageid']})
    return g

def get_path(graph, name1, name2, depth = 5):
    result = cypher.execute("MATCH s = shortestPath((p:Article)-[:TO_ARTICLE*1..%d]->(q:Article)) WHERE p.name =~ '(?i)%s' and q.name =~ '(?i)%s' RETURN s as path LIMIT 1" % (depth, name1, name2)).records
    if len(result) == 0:
        return None
    result = result[0].path.nodes
    g = {}
    g['nodes'] = []
    g['edges'] = []
    for idx in range(len(result)):
        tmp = result[idx]
        if idx == 0:
            g['nodes'].append({'id': tmp['pageid'], 'label': tmp['name'], 'x': idx, 'y': random.random()*10, 'size': 1})
        else:
            g['nodes'].append({'id': tmp['pageid'], 'label': tmp['name'], 'x': idx, 'y': random.random()*10, 'size': 1})
            g['edges'].append({'id': str(idx), 'source': result[idx-1]['pageid'], 'target': tmp['pageid']})
    return g

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET'])
def index():
    g = get_neighbors(graph, name = None, n_neighbors = 100)
    return render_template('neighbors_result.html', graph = json.dumps(g))

@app.route('/neighbors', methods=['GET', 'POST'])
def neighbors():
    form = NameForm()
    if form.validate_on_submit():
        name1 = re.sub(' +', '_', form.name1.data)
        name2 = re.sub(' +', '_', form.name2.data)
        if name2 == '':
            g = get_neighbors(graph, name1)
            if g is None:
                flash(Markup('Root node not found!'))
                return redirect(url_for('neighbors'))
            else:
                session['graph'] = g
                return redirect(url_for('neighbors_result'))
        else:
            g = get_path(graph, name1, name2)
            if g is None:
                flash(Markup('Path not found!'))
                return redirect(url_for('neighbors'))
            else:
                session['graph'] = g
                return redirect(url_for('neighbors_result'))
    return render_template('neighbors.html', form = form)

@app.route('/neighbors_result')
def neighbors_result():
    g = session.get('graph')
    return render_template('neighbors_result.html', graph = json.dumps(g))

if __name__ == '__main__':
    manager.run()
