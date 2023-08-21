#coding=utf-8
from web3 import Web3
import json,requests,random
import time,math,sys
import threading

def getJSONFile(filePath):
    obj = json.load(open(filePath, 'r', encoding='utf-8'))
    return obj

def getLocalLastRound():
    f = open("./record_random", 'r', encoding='utf-8')
    roundId = f.read()
    f.close()
    return int(roundId)

def saveLocalLastRound(last_round):
    f = open('./record_random', 'w')
    f.write(str(last_round))
    f.close()

def rpcLocal(method='net_version',params=[]):
    headers = {'content-type':'application/json'}
    values = {"jsonrpc":"2.0","method":method,"params":params,"id":68}
    data = json.dumps(values)
    response = requests.post(RPC_URL, data = data,headers=headers)
    result = json.loads(response.content)
    # print(result)
    return result["result"]

def rpcLocalBatch(method='net_version',params=[]):
    headers = {'content-type':'application/json'}
    values = []
    for param in params:
        values.append({"jsonrpc":"2.0","method":method,"params":param,"id":68})

    data = json.dumps(values)
    response = requests.post(RPC_URL, data = data,headers=headers)
    result = json.loads(response.content)
    return result

def get_balance(account):
    balance = rpcLocal("eth_getBalance",[account, "latest"])
    return balance

def get_block():
    result = rpcLocal("eth_getBlockByNumber",["latest", False])
    return result["number"]

def get_token_balance(token, account):
    data = "0x70a08231000000000000000000000000" + account.replace("0x","")
    result = rpcLocal("eth_call",[{"to": token, "data": data},"latest"])
    return result

def batch_get_token_balance(token, accounts):
    params = []
    for account in accounts:
        data = "0x70a08231000000000000000000000000" + account.replace("0x","")
        param = [{"to": token, "data": data},"latest"]
        params.append(param)
    result = rpcLocalBatch("eth_call",params)
    return result

def get_current_round():
    result = rpcLocal("eth_call",[{"to": calendar_address, "data": "0xd5c8610c"},"latest"])
    return result

def get_BLOCKS_PER_PERIOD():
    result = rpcLocal("eth_call",[{"to": calendar_address, "data": "0x56412b40"},"latest"])
    return result

def get_GENESIS_BLOCK():
    result = rpcLocal("eth_call",[{"to": calendar_address, "data": "0xddbfc5c6"},"latest"])
    return result

def get_random_seed(round_id):
    data = random_contract_instance.encodeABI(fn_name="getRoundSeed", args=[round_id])
    result = rpcLocal("eth_call",[{"to": random_contract_instance.address, "data": data},"latest"])
    return result

def get_round_tickets(round_id):
    data = tge_contract_instance.encodeABI(fn_name="ROUND_TICKETS", args=[round_id])
    result = rpcLocal("eth_call",[{"to": tge_contract_instance.address, "data": data},"latest"])
    return result

def get_round_oak_day_limit(round_id):
    # result = tge_contract_instance.functions.getRoundBaseInfo(round_id).call()
    data = tge_contract_instance.encodeABI(fn_name="getRoundBaseInfo", args=[round_id])
    result = rpcLocal("eth_call",[{"to": tge_contract_instance.address, "data": data},"latest"])
    return result

def get_round_resulted(round_id):
    data = tge_contract_instance.encodeABI(fn_name="IS_ROUND_RESULTED", args=[round_id])
    result = rpcLocal("eth_call",[{"to": tge_contract_instance.address, "data": data},"latest"])
    return result

def get_randomIndexCount(round_id):
    data = random_contract_instance.encodeABI(fn_name="randomIndexCount", args=[round_id])
    result = rpcLocal("eth_call",[{"to": random_contract_instance.address, "data": data},"latest"])
    return result

def random_with_seed(seed, max_number, size):
    random.seed(seed,version=1)
    a = random.sample(range(0, max_number), size)
    print(len(list(set(a))))
    return a

def random_seed(_from, _to):
    data = random_contract_instance.encodeABI(fn_name = "randomSeed", args=[])
    gasPrice = web3.toWei(GAS_PRICE, 'gwei')
    value = web3.toWei(0, 'ether')
    tx = {
        'from': _from,
        'to': random_contract_instance.address,
        'value': hex(value),
        'gasPrice': hex(gasPrice),
        'data': data
    }
    result = rpcLocal("eth_sendTransaction",[tx])
    print(result)
    return result


def start_check_block():
    block_number = get_block()
    if not block_number:
        print ('No new block')
    else:
        block_number = int(block_number, 16)

    current_round = math.ceil((block_number - start_block)/float(blocks))
    print("Current round: ", current_round)
    last_round = current_round -1
    print("Need to process round: ", last_round)

    local_roundId = getLocalLastRound()
    
    global timer
    timer = threading.Timer(LOOP_TIME, check_block)
    timer.start()

    if last_round > local_roundId:
        print("The new round reached")
        startProcess(last_round)

def startProcess(last_round):
    if not round_status.get(last_round, None):
        round_status[last_round] = True
        try:
            round_base_info = get_round_oak_day_limit(last_round)
            round_base_info = round_base_info.replace("0x","")
            dayLimit = "0x" + round_base_info[0:DECODE_DATA_LENGTH][DECODE_VALUE_INDEX:]
            dayLimit = int(dayLimit, 16)
            print("Round tickets limit: ",dayLimit)

            round_tickets = int(get_round_tickets(last_round), 16)
            print(round_tickets)
            print("Current round " +str(last_round)+ " tickets: ",round_tickets)
            generated_random_seed = get_random_seed(last_round)
            print("Current round seed: ", generated_random_seed)

            if generated_random_seed == "0x0000000000000000000000000000000000000000000000000000000000000000":
                # random_seed(from_address, round_random_address)
                raise Exception("Sorry, you should check the result later after someone generated the seed")

            max_number = round_tickets
            size = dayLimit
            need_to_fill_random = round_tickets > dayLimit
            if need_to_fill_random:
                indexes = random_with_seed(generated_random_seed, max_number, size)
                print("Selected tickets in current round: ", indexes)
            else:
                print("All user has been selected in current round")

            saveLocalLastRound(last_round)
            print(getLocalLastRound())
            round_status[last_round] = True

        except Exception as e:
            print(e)
            round_status[last_round] = False
        

round_status = {}
config = getJSONFile("./config.json")

RPC_URL = config["RPC_URL"]
LOOP_TIME = config["LOOP_TIME"]
GAS_PRICE = config["GAS_PRICE"]

DECODE_DATA_LENGTH = 64
DECODE_VALUE_INDEX = 43


web3 = Web3(Web3.HTTPProvider(RPC_URL))

round_random_address = web3.toChecksumAddress(config["random_contract_address"])
calendar_address = web3.toChecksumAddress(config["calendar_contract_address"])
tge_contract_address = web3.toChecksumAddress(config["tge_contract_address"])


from_address = config["admin1"]["address"]
round_random_abi = getJSONFile("./random_abi.json")
tge_abi = getJSONFile("./tge_abi.json")

random_contract_instance = web3.eth.contract(address=round_random_address, abi=round_random_abi)
tge_contract_instance = web3.eth.contract(address=tge_contract_address, abi=tge_abi)

blocks = int(get_BLOCKS_PER_PERIOD(), 16)
start_block = int(get_GENESIS_BLOCK(), 16)

print(blocks, start_block)

start_check_block()


