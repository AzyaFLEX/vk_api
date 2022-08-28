from functools import lru_cache
import configparser
import vk_api


def get_config(filename):
    _config = configparser.ConfigParser()
    _config.read(filename)
    return _config


def create_session(_config):
    session = vk_api.VkApi(token=_config['account']['token'])
    _vk = session.get_api()
    return _vk


def get_chat_id_by_name(_vk, name='') -> dict:
    _data = _vk.messages.searchConversations(q=name, count=1)['items'][0]
    return _data['peer']['local_id']


def get_chat_users(_vk, chat_id) -> list:
    return list(_vk.messages.getChatUsers(chat_id=chat_id))


def get_public_list(_vk, user_list: list) -> dict:
    _data = {}
    for user_id in user_list:
        try:
            public_id_list = _vk.users.getSubscriptions(user_id=user_id, extended=0)['groups']['items']
            for group_id in public_id_list:
                if group_id not in _data:
                    _data[group_id] = 0
                _data[group_id] += 1
        except vk_api.exceptions.ApiError:
            pass
    return {elm: _data[elm] for elm in sorted(_data, key=lambda x: 1 / _data[x])}


def get_group_name(_vk, _id):
    _data = _vk.groups.getById(group_id=_id)
    return _data[0]['name']


def show_list(_vk, _data: dict) -> None:
    for index, elm in enumerate(list(_data)[:100]):
        print(f'{index + 1}. {get_group_name(_vk, elm)} - {_data[elm]}')


def get_top_public_list():
    _config = get_config('config.ini')
    _vk = create_session(_config)
    show_list(_vk, get_public_list(_vk, get_chat_users(_vk, chat_id=_config['group']['id'])))


@lru_cache()
def get_users_name_by_id(_vk, user_id):
    data = _vk.users.get(user_ids=user_id)[0]
    return f'{data["first_name"]} {data["last_name"]} ({user_id})'


def find_connection(_vk, main_id, start_id, white_list: list = None, black_list: list = None, max_length=4):
    def print_chain(_chain: list):
        print(" -> ".join(map(lambda _id: get_users_name_by_id(_vk, _id), _chain + [main_id])))

    @lru_cache()
    def get_user_friends(_id):
        return _vk.friends.get(user_id=_id)['items']

    queue = [[start_id]]
    check = _vk.friends.get(user_id=main_id)['items']

    if black_list is None:
        black_list = []
    if white_list is None:
        white_list = []

    if start_id in check:
        print(f'{get_users_name_by_id(_vk, start_id)} -> {get_users_name_by_id(_vk, main_id)}')
        check.remove(start_id)

    while queue and len(min(queue, key=len)) <= max_length:
        for chain in queue[:]:
            try:
                for user_id in get_user_friends(chain[-1]):
                    if user_id not in chain and user_id not in black_list:
                        if user_id in check and (True if not white_list else user_id in white_list):
                            print_chain(chain + [user_id])
                        if user_id != main_id:
                            queue.append(chain + [user_id])
            except vk_api.exceptions.ApiError:
                pass
            queue.remove(chain)


if __name__ == '__main__':
    config = get_config('config.ini')
    vk = create_session(config)
    find_connection(vk, 291642276, 216441677)
