import random
import string
import flask
from web3 import Web3
from flask import request, url_for, send_file
import json
import os, codecs
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename, safe_join

HTTP_url = "http://127.0.0.1:8545"
contract_address = "0xadcCBCF42f27fA6709e2013Ac80d4E38Cbd55d91"
owner = ""
with open('golos.abi') as f:
    abi = json.load(f)

SESSION_TYPE = 'filesystem'
UPLOAD_FOLDER = 'F:/ETHER/data/files'
ALLOWED_EXTENSIONS = {'txt'}

app = flask.Flask(__name__)

def create_accounts(file, vote):
    s = file.readlines()
    with open(UPLOAD_FOLDER+'/accounts.txt', "w") as txt:
        for line in s:
            letters = string.ascii_letters
            pwd = ''.join(random.choice(letters) for i in range(10))
            name = line.strip()
            acc = createAcc(pwd)
            tx = {
                "from": w3.eth.defaultAccount,
                "to": acc,
                "value": w3.toWei(0.001, "ether"),
                "gas": 21000,
                "chainId": 98760
            }
            w3.eth.sendTransaction(tx)
            contract.functions.addIzbir(acc, int(vote), name).call()
            tx = contract.functions.addIzbir(acc, int(vote), name).transact()
            w3.eth.waitForTransactionReceipt(tx)
            txt.write(line.strip() + '        ' + acc + '        ' + pwd + '\n')
    return "accounts.txt"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def createAcc(password):
    old = w3.eth.defaultAccount
    w3.eth.defaultAccount = owner
    name = w3.geth.personal.newAccount(password)
    w3.eth.defaultAccount = old
    return name

@app.route('/', methods=['GET', 'POST'])
def auth():
    if request.method == "POST":
        name = request.form.get('name')
        psw = request.form.get('psw')
        vote = request.form.get('vote')
        if (w3.geth.personal.unlockAccount(w3.toChecksumAddress(name), psw, 100000)):
            w3.eth.defaultAccount = w3.toChecksumAddress(name)
            if (w3.eth.defaultAccount == w3.toChecksumAddress(owner)):
                return flask.redirect(url_for("index", vote=vote))
            if contract.functions.checkIzb(w3.eth.defaultAccount, int(vote)).call():
                return flask.redirect(url_for("izbir_index", vote=vote))
            if contract.functions.checkMem(w3.eth.defaultAccount, int(vote)).call():
                return flask.redirect(url_for('member_index', vote=vote))
    else:
        return flask.render_template("auth.html")

@app.route('/index/<string:vote>')
def index(vote):
     return flask.render_template("index.html", account='Администратор', vote=vote)

@app.route('/member_index/<string:vote>')
def member_index(vote):
    return flask.render_template("member_index.html", account='Член комиссии', vote=vote)

@app.route('/izbir_index/<string:vote>')
def izbir_index(vote):
    return flask.render_template("izbir_index.html", account='Избиратель', vote=vote)

@app.route('/get_izbir/<string:vote>', methods = ['GET', 'POST'])
def get_izbir(vote):
    if request.method == 'POST':
        if 'textfile' not in request.files:
            return flask.redirect(request.url)
        file = request.files['textfile']
        if file.filename == '':
            return flask.redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            f = codecs.open(UPLOAD_FOLDER + '/' + filename, 'r',encoding="utf-8")
            new = create_accounts(f, vote)
            safe_path = safe_join(app.config['UPLOAD_FOLDER'], new)
            try:
                return send_file(safe_path, as_attachment=True)
            except FileNotFoundError:
                abort(404)
    return flask.render_template("get_izbir.html", vote=vote)

@app.route('/add_vote', methods=['GET','POST'])
def add_vote():
    if request.method == "POST":
        vname = request.form.get('name')
        vdate = request.form.get('date')
        vote = contract.functions.addVote(vdate, vname).call()
        tx = contract.functions.addVote(vdate, vname).transact()
        w3.eth.waitForTransactionReceipt(tx)
        return flask.render_template('add_vote.html', status = "Голосование добавлено", vote=vote)
    else:
        return flask.render_template('add_vote.html')

@app.route('/results/<string:vote>')
def results(vote):
    results = contract.functions.getResults(int(vote)).call()
    return flask.render_template("results.html", results=results, vote=vote)

@app.route('/golosovanie/<string:vote>', methods = ["GET", "POST"])
def golosovanie(vote):
    if request.method == "POST":
        candidate = request.form['radiobtn']
        contract.functions.golosovanie(int(vote), w3.eth.defaultAccount, int(candidate)).call()
        tx = contract.functions.golosovanie(int(vote), w3.eth.defaultAccount, int(candidate)).transact()
        w3.eth.waitForTransactionReceipt(tx)
        results = contract.functions.getResults(int(vote)).call()
        return flask.redirect(url_for('results', vote=vote, results=results))
    else:
        names, indexes = contract.functions.getCandidates(int(vote)).call()
        candidates = dict(zip(names,indexes))
        return flask.render_template("golosovanie.html", names=candidates, vote=vote)

@app.route('/add_member', methods = ['GET', "POST"])
def add_member():
    if flask.request.method == 'POST':
        pwd = flask.request.form['pwd']
        avote = flask.request.form['vote']
        pwd2 = flask.request.form['pwd2']
        if pwd == pwd2:
            acc = w3.geth.personal.newAccount(pwd)
            tx = {
                "from": w3.eth.defaultAccount,
                "to": acc,
                "value": w3.toWei(10,"ether"),
                "gas": 21000,
                "chainId": 98760
            }
            w3.eth.sendTransaction(tx)
            contract.functions.addMember(acc, int(avote)).call()
            tx = contract.functions.addMember(acc, int(avote)).transact()
            w3.eth.waitForTransactionReceipt(tx)
            return flask.render_template("add_member.html", address = acc)
        else:
            return flask.render_template("add_member.html", address = "Пароли не совпадают")
    else:
        return flask.render_template("add_member.html")

@app.route('/add_izbir', methods=['GET', 'POST'])
def add_izbir():
    if flask.request.method == 'POST':
        name = flask.request.form['name']
        pwd = flask.request.form['pwd']
        vote = flask.request.form['vote']
        pwd2 = flask.request.form['pwd2']
        if pwd == pwd2:
            acc = createAcc(pwd)
            tx = {
                "from": w3.eth.defaultAccount,
                "to": acc,
                "value": w3.toWei(0.1, "ether"),
                "gas": 21000,
                "chainId": 98760
            }
            w3.eth.sendTransaction(tx)
            contract.functions.addIzbir(acc, int(vote), name).call()
            tx = contract.functions.addIzbir(acc, int(vote), name).transact()
            w3.eth.waitForTransactionReceipt(tx)
            return flask.render_template("add_izbir.html", address=acc)
        else:
            return flask.render_template("add_izbir.html", address="Пароли не совпадают")
    else:
        return flask.render_template("add_izbir.html")

@app.route('/add_candidate/<string:vote>', methods=['GET', 'POST'])
def add_candidate(vote):
    if flask.request.method == 'POST':
        name = flask.request.form['name']
        print(w3.eth.defaultAccount)
        contract.functions.addCandidate(name, int(vote)).call()
        tx = contract.functions.addCandidate(name, int(vote)).transact()
        w3.eth.waitForTransactionReceipt(tx)
        return flask.render_template("add_candidate.html", vote=vote)
    else:
        return flask.render_template("add_candidate.html", vote=vote)

if (__name__ == '__main__'):
    w3 = Web3(Web3.HTTPProvider(HTTP_url))
    contract = w3.eth.contract(address=contract_address, abi=abi)
    owner = w3.eth.accounts[0]
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = SESSION_TYPE
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

    app.run(debug=True)
