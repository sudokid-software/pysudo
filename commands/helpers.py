from time import sleep
import secrets

from http_lib import get
import response_msgs


def suggest(irc, _user, msg):
    suggestion = msg[9:]

    irc.suggestions.append(suggestion)
    irc.send_msg(f'The suggestion: {suggestion}')


def reset_suggestions(irc, user, _msg):
    if not irc.check_user(user):
        return

    irc.suggestions = []
    irc.send_msg('Suggestions have been reset!')


def vote_reset(irc, user, _msg):
    if not irc.check_user(user):
        return

    irc.viewers_voted = set()
    irc.votes = {}
    irc.transport.write('The vote has been reset!')


def start_vote(irc, user, msg):
    if user != irc.nick:
        return

    choices = msg.split(' ')[1:]

    irc.votes = {choice: 0 for choice in choices}

    irc.send_msg('The choices are as follows')
    for choice in choices:
        irc.send_msg(f'!vote {choice}')


def vote(irc, user, msg):
    if user in irc.viewers_voted:
        irc.send_msg(f'{user} you have already voted!')
        return

    vote = msg[6:]
    if vote not in irc.votes:
        irc.send_msg(f'{user} you didn\'t provide a valid vote!')
        return

    irc.viewers_voted.add(user)
    irc.votes[vote] += 1
    irc.send_msg(f'{user} you have voted for {vote}!')


def end_vote(irc, user, _msg):
    if not irc.check_user(user):
        return

    vote = None
    value = 0
    for k, v in irc.votes.items():
        if v > value:
            value = v
            vote = k

    irc.send_msg(f'{vote} has won with a total of {value} votes!')


def random_viewer(irc, user, _msg):
    if not irc.check_user(user):
        print(f'{user} are not a valid mod')
        return

    if len(irc.viewers) <= 0:
        irc.update_viewers(user)

    viewers = list(irc.viewers - {'sudokid'})

    r_user = secrets.choice(viewers)

    irc.send_msg(f'{r_user} was selected!')


def update_viewers(irc, user, _msg):
    print(user)
    if not irc.check_user(user):
        return

    response = None
    chatters = None
    counter = 0
    while chatters is None or counter == 100:
        response = get(
            'http://tmi.twitch.tv/group/user/sudokid/chatters')
        chatters = response.get('chatters', None)
        print(response)
        counter += 1
        sleep(10)

    mods = set(response.get('chatters', {}).get('moderators', []))
    viewers = set(response.get(
        'chatters', {}).get('viewers', []))

    irc.mods |= mods
    irc.viewers |= mods
    irc.viewers |= viewers

    print('Mods:', irc.mods)
    print('Viewers:', irc.viewers)
    print('Viewers and mods have been updated')


def add_mod(irc, requester, msg):
    try:
        user = msg.split(' ')[1]
    except IndexError:
        return irc.send_msg('You must provide a username!')

    if irc.check_user(requester):
        irc.mods.add(user.lower())
        irc.send_msg(response_msgs.addmod.format(user=user))
    else:
        irc.send_msg(response_msgs.youre_not_a_mod.format(
            user=requester))


def remove_mod(irc, requester, msg):
    try:
        user = msg.split(' ')[1]
    except IndexError:
        return irc.send_msg('You must provide a username!')

    if requester in irc.admin:
        irc.mods.remove(user.lower())
        irc.send_msg(response_msgs.addmod.format(user=user))
    else:
        irc.send_msg(response_msgs.youre_not_a_mod.format(
            user=requester))


def roll(irc, _user, _msg):
    irc.send_msg(
        'You rolled a ' +
        str(secrets.randbelow(101)))
