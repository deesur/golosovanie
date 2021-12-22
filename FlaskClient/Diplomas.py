from eth_utils import address
import flask
from web3 import Web3
import json


infura_url = 'https://ropsten.infura.io/v3/53248c267d324aa08c4b04ad8acd4550'
contract_address = '0x7C8C714Cfd52DED33D3496277Ebdf100068ca01e'
private_key = '59185ea1d608dd12a9ae3508cdb1ccb7cf51aa2041d4a1f68eaa6418839af601'
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


@app.route('/addrequest', methods=['GET', 'POST'])
def get_address():
    if flask.request.method == 'POST':
        # result = contract.functions.InquireDiplomaByFIO(flask.request.form['FIO']).transact(
        #     {'from': w3.toChecksumAddress(flask.request.form['address']),
        #      'gas': 1000000,
        #      'value': w3.toWei(2, 'finney')
        # })
        address = w3.toChecksumAddress(flask.request.form['address'])
        nonce = w3.eth.getTransactionCount(address)
        tr = contract.functions.InquireDiplomaByFIO(flask.request.form['FIO']).buildTransaction({
            'nonce': nonce,
            'from': address,
            'gas': 3000000,
            'value': w3.toWei(2, 'finney')
        })

        signed_tr = w3.eth.account.signTransaction(tr, private_key=private_key)
        w3.eth.waitForTransactionReceipt(w3.eth.sendRawTransaction(signed_tr.rawTransaction))
    return flask.render_template('addresses.html')


if (__name__ == '__main__'):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    with open ('diplomas.abi') as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=contract_address, abi=abi)

    app.run(debug=True)
