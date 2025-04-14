
from django.utils.translation import gettext as _

def create_tournament_tevent_and_team(user):
    from core.models import Tournament, TournamentPlayer, Team
    from core.tests.test_models import create_user, create_tevent
    """ Create one team for a tevent with two players """
    t = Tournament.objects.create(name='Escalerilla', teams_n=2)
    player1 = user.baseplayer
    esc_player1 = TournamentPlayer.objects.create(tournament=t, player=player1)
    user2 = create_user('user2@example.com', 'pass123')
    player2 = user2.baseplayer
    esc_player2 = TournamentPlayer.objects.create(tournament=t, player=player2)

    tevent = create_tevent(user, t)

    new_team = Team.objects.create(tevent=tevent)
    players = [esc_player1, esc_player2]
    for player in players:
        new_team.players.add(player)
    new_team.save()
    return new_team



def create_tevent_schema(teams):
    """
    Creates the fixture for a tevent with an even ammount of teams

    args: receives a list of teams id's

    returns a list of lists with all rounds and all vs all schema
    """
    n = len(teams)
    if n % 2 != 0:
        raise ValueError(_("The ammount of teams must be even"))

    fixture = []

    rotables = teams[1:]  # team 0 excluded from rotable

    for round in range(n - 1): # ROUNDS PER DAY
        print(f'round {round}')
        round_matches = []
        round_matches.append((teams[0], rotables[round]))  # Equipo fijo vs. equipo de la round

        for i in range(1, n // 2): #MATCHES PER ROUND
            print(f'round - {i} =', (round - i), f'round + {i} = ', rotables[(round + i) % (n-1)])
            round_matches.append((rotables[ (round - i) % (n-1)], rotables[(round + i) % (n-1)]))
        fixture.append(round_matches)
        print('Round matches: ',round_matches)
    return fixture

