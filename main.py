import configparser
import vk_api


def get_chat_id_by_name(_vk, name='') -> dict:
    _data = _vk.messages.searchConversations(q=name, count=1)['items'][0]
    return _data['peer']['local_id']


def get_chat_users(_vk, chat_id) -> list:
    return list(_vk.messages.getChatUsers(chat_id=chat_id))


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    session = vk_api.VkApi(token=config['account']['token'])
    vk = session.get_api()

    data = get_chat_users(vk, chat_id=config['group']['id'])
