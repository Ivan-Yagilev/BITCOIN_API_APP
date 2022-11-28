import datetime
import config
import pydantic_models
import bit
from database.db import *


@db_session
def create_wallet(user: pydantic_models.User = None, private_key: str=None, testnet: bool=False):
    # Test Wallet?
    if not testnet:
        raw_wallet = bit.Key() if not private_key else bit.Key(private_key)
    else:
        raw_wallet = bit.PrivateKeyTestnet() if not private_key else bit.PrivateKeyTestnet(private_key)
    if user:
        wallet = Wallet(user=user, private_key=raw_wallet.to_wif(), address=raw_wallet.address)
    else:
        wallet = Wallet(private_key=raw_wallet.to_wif(), address=raw_wallet.address)
    flush()
    return wallet


@db_session
def create_user(tg_id: int, nick: str = None):
    if nick:
        user = User(tg_ID=tg_id, nick=nick, create_date=datetime.now(), wallet=create_wallet())
    else:
        user = User(tg_ID=tg_id, create_date=datetime.now(), wallet=create_wallet())
    flush()
    return user


@db_session
def create_transaction(
    sender: User,
    amount_btc_without_fee: float,
    receiver_address: str,
    fee: float | None = None,
    testnet: bool = False
):
    """
    :param amount_btc_without_fee:  количество биткоинов исключая комиссию, значение в сатоши
    :param receiver_address: адрес получателя, строка с адресом
    :param amount_btc_with_fee: количество биткоинов включая комиссию, значение в сатоши
    :param fee: абсолютная комиссия, исчисляем в сатоши - необязательно.
    :param testnet: в тестовой сети ли мы работаем
    :return: Transaction object
    """

    wallet_of_sender = bit.Key(sender.wallet.private_key) if not testnet else bit.PrivateKeyTestnet(sender.wallet.private_key)
    sender.wallet.balance = wallet_of_sender.get_balance()
    if not fee:
        fee = bit.network.fees.get_fee() * 1000     # стоимость транзакции sat/B*1000
    amount_btc_with_fee = amount_btc_without_fee + fee
    if amount_btc_without_fee + fee > sender.wallet.balance:
        return f"Too low balance: {sender.wallet.balance}"
    
    output = [(receiver_address, amount_btc_without_fee, 'satoshi')]
    
    # send transaction
    tx_hash = wallet_of_sender.send(output, fee, absolute_fee=True)     
    
    # saving transaction in db
    transaction = Transaction(sender=sender,
                              sender_wallet=sender.wallet,
                              fee=fee,
                              sender_address=sender.wallet.address,
                              receiver_address=receiver_address,
                              amount_btc_with_fee=amount_btc_with_fee,
                              amount_btc_without_fee=amount_btc_without_fee,
                              date_of_transaction=datetime.now(),
                              tx_hash=tx_hash)
    return transaction.to_dict()


@db_session
def update_wallet_balance(wallet: pydantic_models.Wallet):
    # Testet?
    testnet = False if not wallet.private_key.startswith('c') else True
    bit_wallet = bit.Key(wallet.private_key) if not testnet else bit.PrivateKeyTestnet(wallet.private_key)
    wallet.balance = bit_wallet.get_balance()
    return wallet


@db_session
def update_all_wallets():
    for wallet in select(w for w in Wallet)[:]: 
        update_wallet_balance(wallet)
        print(wallet.address, wallet.balance)
    return True


@db_session
def get_user_by_id(id: int):
    return User[id]


@db_session
def get_user_by_tg_id(tg_id: int):
    return User.select(lambda u: u.tg_ID == tg_id).first()


@db_session
def get_transaction_info(transaction: pydantic_models.Transaction):
    return {"id": transaction.id,
            "sender": transaction.sender if transaction.sender else None,
            "receiver": transaction.receiver if transaction.receiver else None,
            "sender_wallet": transaction.sender_wallet if transaction.sender_wallet else None,
            "receiver_wallet": transaction.receiver_wallet if transaction.receiver_wallet else None,
            "sender_address": transaction.sender_address,
            "receiver_address": transaction.receiver_address,
            "amount_btc_with_fee": transaction.amount_btc_with_fee,
            "amount_btc_without_fee": transaction.amount_btc_without_fee,
            "fee": transaction.fee,
            "date_of_transaction": transaction.date_of_transaction,
            "tx_hash": transaction.tx_hash}


@db_session
def get_wallet_info(wallet: pydantic_models.Wallet):
    wallet = update_wallet_balance(wallet)
    return {"id": wallet.id if wallet.id else None,
            "user": wallet.user if wallet.user else None,
            "balance": wallet.balance if wallet.balance else None,
            "private_key": wallet.private_key if wallet.private_key else None,
            "address": wallet.address if wallet.address else None,
            "sended_transactions": wallet.sended_transactions if wallet.sended_transactions else [],
            "received_transactions": wallet.received_transactions if wallet.received_transactions else []}


@db_session
def get_user_info(user: pydantic_models.User):
    return {"id": user.id,
            "tg_ID": user.tg_ID if user.tg_ID else None,
            "nick": user.nick if user.nick else None,
            "create_date": user.create_date,

            "wallet": get_wallet_info(user.wallet),
            "sended_transactions": user.sended_transactions if user.sended_transactions else [],
            "received_transactions": user.received_transactions if user.received_transactions else []}


@db_session
def update_user(user: pydantic_models.User_to_update):
    user_to_update = User[user.id]
    if user.tg_ID:
        user_to_update.tg_ID = user.tg_ID
    if user.nick:
        user_to_update.nick = user.nick
    if user.create_date:
        user_to_update.create_date = user.create_date
    if user.wallet:
        user_to_update.wallet = user.wallet
    return user_to_update
