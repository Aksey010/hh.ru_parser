import requests
from json import dump


def hh_parser(vacancy,city):

    #  Юзер-агент
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
              }

    #  url сайта
    url_vacancies = 'https://api.hh.ru/vacancies'

    # Ввод текста для поиска
    # vacancy = input(f'Введите вакансию/ии: ')
    # city = input(f'Введите город/а: ')


    vacancy_city = vacancy + ' AND ' + city

    #  Параметры запроса
    params = {'text': vacancy_city,
              'per_page': 50,
              'page': 1}


    # Запрос
    result = requests.get(url_vacancies, params=params, headers=headers).json()

    count_pages = result['pages']  # Количество страниц
    count = 0  # Количество найденных вакансий
    salary = {'salary': {'from': 0, 'to': 0}}  # Зарплата от и до
    c_f = 0  # Переменная для вычисления среднего значения зарплаты from
    c_t = 0  # Переменная для вычисления среднего значения зарплаты to
    requirements = {}  # Переменная для всех требуемых навыков
    best_skill = {}  # Переменная для самых нужных навыков

    want_pages = 2
    # while True:
    #     try:
    #         want_pages = int(input(f'Введите количество страниц, которые будут обрабатываться (всего{count_pages})'))  # Переменная определения кол-ва обрабатываемых страниц
    #         if 1 <= want_pages <= count_pages:
    #             break
    #     except: print(f'Вы ввели неверное значение')

    print(f'Обработка вакансий начата. Всего страниц: {want_pages}')

    # Получение средней зарплаты, количества вакансий, необходимых навыков для каждой страницы
    for i in range(1,want_pages+1):
        print(f'Страница номер {i}')
        params = {'text': vacancy_city,
                  'per_page': 50,
                  'page': i}

        print(f'Получение страницы')
        result = requests.get(url_vacancies, params=params).json()
        print(f'Выполнено!')

        print(f'Получение количества вакансий')
        count += result['found']  # Получение количества вакансий
        print(f'Выполнено!')

        print(f'Получение необходимых навыков и средней зарплаты')
        for item in result['items']:

            req_url = item['url']
            req_result = requests.get(req_url).json()
            try:
                for name in req_result['key_skills']:
                    if name['name'].lower() not in requirements:
                        requirements[name['name'].lower()] = 1
                    else:
                        requirements[name['name'].lower()] += 1  # Получение необходимых навыков
            except:
                pass

            try:
                if salary['salary']['from'] is not None:
                    salary['salary']['from'] += item['salary']['from']
                    c_f += 1
                if salary['salary']['to'] is not None:
                    salary['salary']['to'] += item['salary']['to']
                    c_t += 1
            except:
                pass
        print(f'Выполнено!')

    try:
        salary['salary']['from'] = int(salary['salary']['from'] / c_f)  # Получение средней зарплаты

    except ZeroDivisionError:
        salary['salary']['from'] = 'Нет информации'

    try:
        salary['salary']['to'] = int(salary['salary']['to'] / c_t)  # Получение средней зарплаты
    except ZeroDivisionError:
        salary['salary']['to'] = 'Нет информации'

    # Получение несколько (5) самых нужных навыков
    try:
        for i in range(5):
            best_skill[max(requirements)] = requirements[max(requirements)]
            del requirements[max(requirements)]
    except:
        best_skill = 'Нет информации'

    # Составление сообщения
    report = {'keywords': vacancy_city,   # Введёный запрос
              'count': count,             # Кол-во найденных записей
              'mean_salary': salary,      # Средняя зарплата
              'requirements': best_skill  # Самые нужные навыки
              }


    with open('result.json', mode='w') as f:
        dump(report, f)


if __name__ == '__main__':

    hh_parser('Строитель', 'Москва')
