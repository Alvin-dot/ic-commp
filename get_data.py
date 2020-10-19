import requests


def get_data_from_api(start_time, end_time, feed_id=506, interval=60, interval_type=1,
                      apikey='e9211b9101e5b2f654e7092611589d06', skip_missing=1, export=1):

    """
    # Id do feed requerido
    feed_id = 506
    # Tempo inicial (UNIXTIME em ms)
    start_time = 1603132200000
    # Tempo final (UNIXTIME em ms)
    end_time = 1603134307000
    # Especifica ação para missing data (0 = coloca NoneType | 1 = não coloca NoneType)
    skip_missing = 0
    # Indica o tamanho da data (0 = mais data | 1 = menos data)
    export = 1
    # Valor do intervalo entre os dados
    interval = 30
    # Seleciona o tipo do intervalo (0 = seconds | 1 = samples per second)
    inteval_type = 1
    # Chave da API
    apikey = 'e9211b9101e5b2f654e7092611589d06'
    """

    data = requests.get(f"https://vega.eletrica.ufpr.br/emoncms/feed/data.json?"
                        f"id={feed_id}"
                        f"&start={start_time}"
                        f"&end={end_time}"
                        f"&interval={interval}"
                        f"&skipmissing={skip_missing}"
                        f"&apikey={apikey}"
                        f"&intervaltype={interval_type}"
                        f"&export={export}")

    return data.json()
