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


def get_group_name(_vk, id):
    _data = _vk.groups.getById(group_id=id)
    return _data[0]['name']


def show_list(_vk, _data: dict) -> None:
    for index, elm in enumerate(list(_data)[:100]):
        print(f'{index + 1}. {get_group_name(_vk, elm)} - {_data[elm]}')


if __name__ == '__main__':
    config = get_config('config.ini')
    vk = create_session(config)
    show_list(vk, get_public_list(vk, get_chat_users(vk, chat_id=config['group']['id'])))
