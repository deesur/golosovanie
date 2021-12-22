# from eth_utils import address
from eth_utils import address
import flask
from web3 import Web3, method
import json
import datetime


infura_url = 'https://ropsten.infura.io/v3/53248c267d324aa08c4b04ad8acd4550'
contract_address = '0x7C8C714Cfd52DED33D3496277Ebdf100068ca01e'
private_key = '59185ea1d608dd12a9ae3508cdb1ccb7cf51aa2041d4a1f68eaa6418839af601'
address = '0xfeacbB86041aF284D599032CB17D886D3c62f912'

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template("index.html")


# @app.route('/getowner')
# def getowner():
#     owner = contract.functions.GetEmployees().call()
#     return flask.render_template("Owner.html", employees=owner)

@app.route('/getemployees')
def getemployees():
    employees = contract.functions.GetEmployees().call()
    return flask.render_template("employees.html", employees=employees)

@app.route('/getbalance')
def getbalance():
    result = contract.functions.GetBalance().call()
    return flask.render_template("balance.html", balance=result)

@app.route('/getowner')
def getowner():
    owner = contract.functions.getOwner().call()
    return flask.render_template("Owner.html", owner=owner)


@app.route('/getdiploma')
def get_diploma():
    result = contract.functions.InquireDiplomaByNumber('').transact({'from': address, 'value': w3.toWei(2, 'finney')})
    return flask.render_template("Diploma.html", fio=result)

@app.route('/diplomaslist', methods=['GET', 'POST'])
def diplomas_list():
    diplomas = contract.functions.GetResult().call()
    return flask.render_template("diplomas.html", diplomas = diplomas)

@app.route('/adddiploma', methods=['GET', 'POST'])
def add_diploma():
    if flask.request.method == 'POST':
        fio = flask.request.form['fio']
        serial = flask.request.form['serial']
        date = flask.request.form['date']
        tr = contract.functions.AddDiploma(fio, serial, date).call()
    return flask.render_template("add_diploma.html", fio = tr)

@app.route('/inquire_diploma', methods=['GET', 'POST'])
def inquire_diploma():
    return flask.render_template('inquire_diploma.html')


if (__name__ == '__main__'):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    w3.eth.default_account = address
    with open ('diplomas.abi') as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=contract_address, abi=abi)

    app.run(debug=True)
