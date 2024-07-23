import requests
from json import dump
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from SQLAlchemy import Requirements, Skills, Search

def hh_parser(vacancy, city):

    engine = create_engine('sqlite:///orm.sqlite', echo=True)
    engine.connect()
    Session = sessionmaker(bind=engine)
    sess = Session()


    #  Юзер-агент
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
              }

    #  url сайта
    url_vacancies = 'https://api.hh.ru/vacancies'

    # Ввод текста для поиска
    # vacancy = input(f'Введите вакансию/ии: ')
    # city = input(f'Введите город/а: ')

    vacancy_city = vacancy.lower().replace(' ', '') + ' AND ' + city

    #  Параметры запроса
    params = {'text': vacancy_city,
              'per_page': 50,
              'page': 1}

    # Запрос
    result = requests.get(url_vacancies, params=params, headers=headers).json()

    count_pages = result['pages']  # Количество страниц
    count = 0  # Количество найденных вакансий
    from_ = 0                    # Зарплата от и до
    to_ = 0
    c_f = 0  # Переменная для вычисления среднего значения зарплаты from
    c_t = 0  # Переменная для вычисления среднего значения зарплаты to
    requirements = {}  # Переменная для всех требуемых навыков
    best_skill = []  # Переменная для самых нужных навыков

    # Поиск в Search по вакансии и городу
    condition = sess.query(Search).filter_by(vacancy=vacancy, city=city).first()

    # Если вакансия и город не в базе, то ...
    if not condition:

        want_pages = 2
        # while True:
        #     try:
        #         want_pages = int(input(f'Введите количество страниц, которые будут обрабатываться (всего{count_pages})'))  # Переменная определения кол-ва обрабатываемых страниц
        #         if 1 <= want_pages <= count_pages:
        #             break
        #     except: print(f'Вы ввели неверное значение')

        print(f'Обработка вакансий начата. Всего страниц: {want_pages}')

        # Получение средней зарплаты, количества вакансий, необходимых навыков для каждой страницы
        for i in range(1, want_pages + 1):
            print(f'Страница номер {i}')
            params = {'text': vacancy_city,
                      'per_page': 50,
                      'page': i}

            print(f'Получение страницы')
            # result = requests.get(url_vacancies, params=params, timeout=10).json()
            print(f'Выполнено!')

            print(f'Получение количества вакансий')
            count += result['found']  # Получение количества вакансий
            print(f'Выполнено!')

            print(f'Получение необходимых навыков и средней зарплаты')
            for item in result['items']:

                req_url = item['url']
                try:
                    req_result = requests.get(req_url, params=params, timeout=5).json()
                    try:
                        for name in req_result['key_skills']:
                            if name['name'].lower() not in requirements:
                                requirements[name['name'].lower()] = 1
                            else:
                                requirements[name['name'].lower()] += 1  # Получение необходимых навыков
                    except:
                        pass
                except:
                    pass

                try:
                    if item['salary']['from'] is not None:
                        from_ += item['salary']['from']
                        c_f += 1
                    if item['salary']['to'] is not None:
                        to_ += item['salary']['to']
                        c_t += 1
                except:
                    pass
            print(f'Выполнено!')

        try:
            from_ = int(from_ / c_f)  # Получение средней зарплаты

        except ZeroDivisionError:
            from_ = 'Нет информации'

        try:
            to_ = int(to_ / c_t)  # Получение средней зарплаты
        except ZeroDivisionError:
            to_ = 'Нет информации'

        # Получение несколько (5) самых нужных навыков
        try:
            requirements = dict(sorted(requirements.items(), key=lambda item: item[1]))
            best_skill.append(list(requirements)[:5])
            best_skill = best_skill[0]
        except:
            best_skill = 'Нет информации'

        # Вставить в search всё найденное

        sess.add(Search(vacancy, city, count, from_, to_))
        sess.commit()

        world_id = sess.query(Search).all()[-1].world_id

        # Если best_skill не пуст
        if best_skill:

            if best_skill != 'Нет информации':

                for skill in best_skill:
                    sess.add(Skills(skill))
                    s_id = sess.query(Skills).filter_by(name=skill).first().id
                    sess.add(Requirements(world_id, s_id))
            else:
                sess.add(Requirements(world_id, best_skill))

            sess.commit()
            sess.close()

        if not best_skill:
            best_skill = 'Нет информации'

        return vacancy, city, count, from_, to_, best_skill

    # Если запрос в базе
    else:
        data = sess.query(Search).filter_by(vacancy=condition.vacancy, city=condition.city).first()

        id_s = sess.query(Requirements).filter_by(world_id=data.world_id).all()

        skill = []
        for i in id_s:

            skill.append(sess.query(Skills).filter_by(id=i.id).first().name)

        sess.close()

        if not skill:
            skill = 'Нет информации'

        return data.vacancy, data.city, data.count, data.sal_from, data.sal_to, skill





    # # Составление сообщения
    # report = {'vacancy': vacancy,         # Введённая вакансия
    #           'city': city,                # Введённый город
    #           'count': count,             # Кол-во найденных записей
    #           'from': salary['from'],             # Средняя зарплата меньшее значение
    #           'to': salary['to'],
    #           'requirements': best_skill  # Самые нужные навыки
    #           }
    #
    # with open('result.json', mode='w') as f:
    #     dump(report, f)


if __name__ == '__main__':

    # _,_,_,_,_,_ = hh_parser('C++ developer', 'Москва')
    print(hh_parser('das', 'Москва'))

