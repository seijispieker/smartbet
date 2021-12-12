def arbitrage(events):
    arbitrageEvents = {}
    count = 0

    print('Calculating arbitrage bets...')

    for id, event in events.items():
        for market in event['markets'].values():
            arbitrage = 0

            for outcome in market.values():
                arbitrage += 1 / outcome['odds']

            if 0 < arbitrage < 1:
                event['roi (%)'] = ((1 / arbitrage) - 1) * 100
                arbitrageEvents[id] = event
                count += 1

    print(f'Number of arbitrage bets: {count}')
    return arbitrageEvents
