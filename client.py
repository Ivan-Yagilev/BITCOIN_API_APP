import requests
import pydantic_models
from config import api_url


def update_user(user: dict):
    """Обновляем юзера"""
    user = pydantic_models.User_to_update.validate(user)

    responce = requests.put(f'{api_url}/user/{user.id}', data=user.json())
    try:
        return responce.json()
    except:
        return responce.text


def delete_user(user_id: int):
    """
    Удаляем юзера
    :param user_id:
    :return:
    """
    return requests.delete(f'{api_url}/user/{user_id}').json()


def create_user(user: pydantic_models.User_to_create):
    """
    Создаем Юзера
    :param user:
    :return:
    """
    user = pydantic_models.User_to_create.validate(user)
    return requests.post(f'{api_url}/user/create', data=user.json()).json()


def get_info_about_user(user_id):
    """
    Получаем информацию по юзеру
    :param user_id:
    :return:
    """
    return requests.get(f'{api_url}/get_info_by_user_id/{user_id}').json()


def get_user_balance_by_id(user_id):
    """
    Получаем баланс юзера
    :param user_id:
    :return:
    """
    responce = requests.get(f'{api_url}/get_user_balance_by_id/{user_id}')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_total_balance():
    """
    Получаем общий баланс
    :return:
    """
    responce = requests.get(f'{api_url}/get_total_balance')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_users():
    """
    Получаем всех юзеров
    :return list:
    """
    return requests.get(f"{api_url}/users").json()


def get_user_wallet_by_tg_id(tg_id):
    user_dict = get_user_by_tg_id(tg_id)
    return requests.get(f"{api_url}/get_user_wallet/{user_dict['id']}").json()
    

def get_user_by_tg_id(tg_id):
    """
    Получаем юзера по айди его ТГ
    :param tg_id:
    :return:
    """
    return requests.get(f"{api_url}/user_by_tg_id/{tg_id}").json()


def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
    user_dict = get_user_by_tg_id(tg_id)
    payload = {'receiver_address': receiver_address,
               'amount_btc_without_fee': amount_btc_without_fee}
    responce = requests.post(f"{api_url}/create_transaction/{user_dict['id']}", json=payload)
    return responce.text

pydantic_models.User_to_update.update_forward_refs()


print(get_total_balance())