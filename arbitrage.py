def arbitrage(events):
    arbitrageEvents = {}
    count = 0

    print('Calculating arbitrage bets...')

    for id, event in events.items():
        for market in event['markets'].values():
            inverse = 0

            for outcome in market.values():
                inverse += 1 / outcome['odds']

            if 0 < inverse < 1:
                arbitrageEvents[id] = event
                count += 1

    print(f'Number of arbitrage bets: {count}')

    return arbitrageEvents
