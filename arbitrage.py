def arbitrage(events):
    arbitrageEvents = {}
    count = 0

    print('Calculating arbitrage bets...')

    for id, event in events.items():
        for market_name, market in event['markets'].items():
            arbitrage = 0

            if len(market) < 2:
                continue
            if 'draw' in market and len(market) < 3:
                continue

            for outcome in market.values():
                arbitrage += 1 / outcome['odds']

            if 0 < arbitrage < 1:
                roi = ((1 / arbitrage) - 1) * 100
                event['markets'][market_name]['roi (%)'] = roi
                arbitrageEvents[id] = event
                count += 1

    print(f'Number of arbitrage bets: {count}')
    return arbitrageEvents
