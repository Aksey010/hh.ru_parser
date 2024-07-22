import requests
from json import dump
import sqlite3

def hh_parser(vacancy, city):

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

    conn = sqlite3.connect('hh_ru.db', check_same_thread=False)

    cur = conn.cursor()

    search = cur.execute("select vacancy, city from search").fetchall()

    # Если вакансия и город не в базе, то ...
    if (vacancy, city) not in search:

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
            from_ = int( from_ / c_f)  # Получение средней зарплаты

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
        cur.execute("insert into search values(?,?,?,?,?,?)",
                    [None, vacancy, city, count, from_, to_])
        conn.commit()
        # Если best_skill не пуст
        if best_skill:
            # В skills добавляются связки (None,best_skill)
            if best_skill != 'Нет информации':

                data = [(None, best_skill[i]) for i in range(len(best_skill))]
                cur.executemany("insert into skills values(?,?)", data)
                conn.commit()

                # В requirements добавляются world_id и id_skill
                world_id = cur.execute("select world_id from search").fetchall()[-1][0]
                skill_id = []
                skill_world = []

                # print(f'best_skill {best_skill}')

                for i in range(len(best_skill)):
                    one_skill = best_skill[i]
                    # print(f'one_skill {one_skill}')
                    skill_id.append(cur.execute("select id from skills where name= ?", [one_skill]).fetchall()[0][0])
                    skill_world.append((world_id, skill_id[i]))

                # print(f'best_skill {best_skill}')
                # print(f'skill_id {skill_id}')
                # print(f'skill_world {skill_world}')

                cur.executemany("insert into requirements values(?,?)", skill_world)

            conn.commit()
            conn.close()

        skill = best_skill

        return vacancy, city, count, from_, to_, skill

    else:
        count = cur.execute("select count from search where vacancy=? and city=?", [vacancy, city]).fetchall()[0][
            0]  # Кол-во найденных записей
        # print(f'count {count}')
        from_ = cur.execute("select [from] from search where vacancy=? and city=?", [vacancy, city]).fetchall()[0][
            0]  # Средняя зарплата меньшее значение
        # print(f'from_ {from_}')
        to_ = cur.execute("select [to] from search where vacancy=? and city=?", [vacancy, city]).fetchall()[::][0][0]
        # print(f'to_ {to_}')
        world_id = cur.execute("select world_id from search where vacancy=? and city=?", [vacancy, city]).fetchall()[0][0]
        # print(f'world_id {world_id}')
        id_skill = cur.execute("select id_skill from requirements where world_id=?", [world_id]).fetchall()
        # print(f'id_skill {id_skill}')

        skill = []
        for i in range(len(id_skill)):
            skill.append(cur.execute("select name from skills where id=?", id_skill[i]).fetchall()[::][0][0])
        # print(f'skill {skill}')

        cur.close()

        return vacancy, city, count, from_, to_, skill



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

    _,_,_,_,_, skills = hh_parser('Юрист', 'Москва')

