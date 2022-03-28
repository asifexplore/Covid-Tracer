'''
This module encapulsates all functions needed for SQL queries regarding 
complex statements to a MYSQL DB.
@Author: Team 22 ICT2103 2021
'''
import mysql.connector

from constants import *
from datetime import date


def select_count_vaccinated_infected_range(database_client, entities, date_range):
    '''
    Function that get the count for infected and vaccinated based on DATE RANGE and ALL
    return result = count
    '''
    print(date_range)
    if date_range == 0:
        # condition 1 - get count for all vaccinated.
        if entities == 'vaccinated':
            query = f''' SELECT COUNT(citizen_id)
                     FROM {VACCINATION_HISTORY_TABLE_NAME}
                     WHERE (dose_type = 'first_dose' OR dose_type = 'second_dose' OR dose_type = 'booster')  
                '''

        # condition 2 - get count for all infected.
        else:
            query = f''' SELECT COUNT(citizen_id)
                        FROM {HEALTH_HISTORY_TABLE_NAME}
                        WHERE (status = 'infected')
                    '''
    else:
        # condition 3 - get count for specific date range vaccinated.
        if entities == 'vaccinated':
            query = f''' SELECT COUNT(citizen_id)
                     FROM {VACCINATION_HISTORY_TABLE_NAME}
                     WHERE (dose_type = 'first_dose' OR dose_type = 'second_dose' OR dose_type = 'booster') 
                     AND (created_at BETWEEN DATE( DATE_SUB( NOW(), INTERVAL {date_range} DAY)) AND DATE( NOW()) )
                '''

        # condition 4 - get count for specific date range infected.
        else:
            query = f''' SELECT COUNT(citizen_id) 
                     FROM {HEALTH_HISTORY_TABLE_NAME}
                     WHERE (status = 'infected')
                     AND (created_at BETWEEN DATE( DATE_SUB( NOW(), INTERVAL {date_range} DAY)) AND DATE( NOW()) )
                '''

    cursor = database_client.execute_statement(query)
    result = cursor.fetchone()[0]

    return result


def select_percentage_vaccinated_infected_range(database_client, entities, date_range):
    '''
    Function that get the percentage for infected and vaccinated based on DATE RANGE and ALL
    return result = tuple of db [(count filter, total citizens)]
    to be used as (count filter/total citizens) * 100
    '''

    query = ""

    if date_range == ALL_UNIT:
        # condition 1 - get tuple (vaccinated, citizens) for all vaccinated.
        if entities == 'vaccinated':
            query = f''' SELECT (
                            SELECT COUNT(DISTINCT citizen_id)
                            FROM {VACCINATION_HISTORY_TABLE_NAME}
                            WHERE (dose_type = 'first_dose' OR (dose_type = 'second_dose' OR dose_type = 'booster')))
                            AS VaccinatedCount,
                                (   
                            SELECT COUNT(nric) 
                            FROM {CITIZEN_TABLE_NAME})   
                            AS TotalCitizens
                    '''
        # condition 2 - get tuple (infected, citizens) for all infected.
        else:
            query = f''' SELECT (
                        SELECT COUNT(DISTINCT citizen_id)
                        FROM {HEALTH_HISTORY_TABLE_NAME}
                        WHERE (status = 'infected'))
                        AS InfectedCount,
                            (
                        SELECT COUNT(nric)
                        FROM {CITIZEN_TABLE_NAME})
                        AS TotalCitizens
                 '''
    else:
        # condition 3 - get tuple (vaccinated, citizens) for vaccinated based on date range.
        if entities == 'vaccinated':
            query = f''' SELECT (
                            SELECT COUNT(DISTINCT citizen_id)
                            FROM {VACCINATION_HISTORY_TABLE_NAME}
                            WHERE (dose_type = 'first_dose' OR (dose_type = 'second_dose' OR dose_type = 'booster'))
                            AND (created_at BETWEEN DATE( DATE_SUB( NOW(), INTERVAL {date_range} DAY)) AND 
                            DATE( NOW()) )) AS VaccinatedCount, 
                                ( 
                            SELECT COUNT(nric) 
                            FROM {CITIZEN_TABLE_NAME}) 
                            AS TotalCitizens
                    '''

        # condition 4 - get tuple (infected, citizens) for infected based on date range.
        else:
            query = f''' SELECT (
                            SELECT COUNT(DISTINCT citizen_id)
                            FROM {HEALTH_HISTORY_TABLE_NAME}
                            WHERE (status = 'infected')
                            AND (created_at BETWEEN DATE( DATE_SUB( NOW(), INTERVAL {date_range} DAY)) AND DATE( NOW()) ))
                            AS InfectedCount,
                                (
                            SELECT COUNT(nric)
                            FROM {CITIZEN_TABLE_NAME})
                            AS TotalCitizens
                    '''

    cursor = database_client.execute_statement(query)
    result = cursor.fetchall()
    return result


def get_infected_number_by_date_range(database_client, hours=0):

    if hours == 0:
        query = f'''SELECT 
                IF(count(v.created_at) IS NULL, 0, count(v.created_at)) AS Created,
                b.Days AS date
                FROM 
                (SELECT a.Days 
                FROM (
                    SELECT curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a)) DAY AS Days
                    FROM       (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS a
                    CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS b
                    CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS c
                ) a
                WHERE a.Days >= curdate() - INTERVAL 365 DAY ) b
                LEFT JOIN health_historys v
                ON DATE(v.created_at) = b.Days AND v.status = 'infected'
            
                GROUP BY YEAR(date),MONTH(date)
                order by YEAR(date),MONTH(date)
                '''
    elif hours == 8760:
        query = f''' 
                    SELECT 
                    IF(count(v.created_at) IS NULL, 0, count(v.created_at)) AS Created,
                    b.Days AS date
                    FROM 
                    (SELECT a.Days 
                    FROM (
                        SELECT curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a)) DAY AS Days
                        FROM       (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS a
                        CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS b
                        CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS c
                    ) a
                    WHERE a.Days >= curdate() - INTERVAL 365 DAY ) b
                    LEFT JOIN health_historys v
                    ON DATE(v.created_at) = b.Days AND v.status = 'infected'
                
                    GROUP BY YEAR(date),MONTH(date)
                    order by YEAR(date),MONTH(date)
                '''
    else:
        query = f''' 
        select count(v.status),d.date, v.created_at from 
        (select adddate('1970-01-01',t4.i*10000 + t3.i*1000 + t2.i*100 + t1.i*10 + t0.i) date from
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t0,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t1,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t2,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t3,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t4) d
        LEFT JOIN health_historys v on d.date = DATE(v.created_at) AND v.status = 'infected'
        where d.date BETWEEN DATE_SUB(NOW(), INTERVAL {hours} HOUR) AND NOW()
        group by d.date
        order by d.date
                '''
    cursor = database_client.execute_statement(query)

    result = []
    for row in cursor:
        result.append(row)

    return result


def get_vaccine_number_by_date_range(database_client, hours=0):
    print('get_vaccine_number_by_date_range', hours)
    if hours == 0:
        query = f'''SELECT 
                    IF(count(v.created_at) IS NULL, 0, count(v.created_at)) AS Created,
                    b.Days AS date
                    FROM 
                    (SELECT a.Days 
                    FROM (
                        SELECT curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a)) DAY AS Days
                        FROM       (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS a
                        CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS b
                        CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS c
                    ) a
                    WHERE a.Days >= curdate() - INTERVAL (DATEDIFF(curdate(),'2020-01-01')) DAY ) b
                    LEFT JOIN vaccination_historys v
                    ON DATE(v.created_at) = b.Days 

                    GROUP BY YEAR(date),QUARTER(date)
                    order by YEAR(date),QUARTER(date)  
                    '''
    elif hours == 8760:
        query = f''' 
                    SELECT 
                    IF(count(v.created_at) IS NULL, 0, count(v.created_at)) AS Created,
                    b.Days AS date
                    FROM 
                    (SELECT a.Days 
                    FROM (
                        SELECT curdate() - INTERVAL (a.a + (10 * b.a) + (100 * c.a)) DAY AS Days
                        FROM       (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS a
                        CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS b
                        CROSS JOIN (SELECT 0 AS a UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS c
                    ) a
                    WHERE a.Days >= curdate() - INTERVAL 365 DAY ) b
                    LEFT JOIN vaccination_historys v
                    ON DATE(v.created_at) = b.Days 
                
                    GROUP BY YEAR(date),MONTH(date)
                    order by YEAR(date),MONTH(date)
                '''

    else:
        query = f''' 
        select d.date, count(v.created_at), v.created_at from 
        (select adddate('1970-01-01',t4.i*10000 + t3.i*1000 + t2.i*100 + t1.i*10 + t0.i) date from
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t0,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t1,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t2,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t3,
        (select 0 i union select 1 union select 2 union select 3 union select 4 union select 5 union select 6 union select 7 union select 8 union select 9) t4) d
        LEFT JOIN vaccination_historys v on d.date = DATE(v.created_at) 
        where d.date BETWEEN DATE_SUB(NOW(), INTERVAL {hours} HOUR) AND NOW()
        group by d.date
        order by d.date
                '''

    print(query)
    cursor = database_client.execute_statement(query)

    result = []
    for row in cursor:
        result.append(row)

    return result


def get_youngest_oldest_infected(database_client, youngest_oldest, unit):
    ''' 
    Get oldest/youngest citizen infected in last 24hr/ 1 week/ 1month/ 1year/ all
    min = oldest date, max = newest date
    unit day/week/month/year/all
    '''
    if youngest_oldest == OLDEST:
        minmaxdate = 'MIN'
    else:
        minmaxdate = 'MAX'

    if unit == ALL_UNIT:
        cursor = database_client.execute_statement(
            f'''
                SELECT timestampdiff(YEAR,{minmaxdate}(c.date_of_birth),CURRENT_DATE)
                FROM {CITIZEN_TABLE_NAME} AS c,{HEALTH_HISTORY_TABLE_NAME} AS hh
                WHERE c.id = hh.citizen_id
                AND hh.status = 'infected'
                '''
        )
    else:
        cursor = database_client.execute_statement(
            f'''
            SELECT timestampdiff(YEAR,{minmaxdate}(c.date_of_birth),CURRENT_DATE)
            FROM {CITIZEN_TABLE_NAME} AS c,{HEALTH_HISTORY_TABLE_NAME} AS hh
            WHERE c.id = hh.citizen_id
            AND hh.status = 'infected'
            AND DATE(hh.created_at) > DATE(DATE_ADD(NOW(), INTERVAL -1 {unit}));
            '''
        )
    result = cursor.fetchone()
    if result[0] is None:
        return None
    else:
        return result[0]


def youngest_oldest_change(database_client, youngest_oldest, unit, current_age):
    ''' 
    Get oldest/youngest citizen infected change in last 24hr/ 1 week/ 1month/ 1year/ all
    min = oldest date, max = newest date
    unit day/week/month/year/all
    '''
    if youngest_oldest == OLDEST:
        minmaxdate = 'MIN'
    else:
        minmaxdate = 'MAX'

    if current_age is None:
        return '100'
    if unit == 'all':
        cursor = database_client.execute_statement(
            f'''
                SELECT timestampdiff(YEAR,{minmaxdate}(c.date_of_birth),CURRENT_DATE)
                FROM {CITIZEN_TABLE_NAME} AS c,{HEALTH_HISTORY_TABLE_NAME} AS hh
                WHERE c.id = hh.citizen_id
                AND hh.status = 'infected'
                '''
        )
    else:
        cursor = database_client.execute_statement(
            f'''
            SELECT timestampdiff(YEAR,{minmaxdate}(c.date_of_birth),CURRENT_DATE)
            FROM {CITIZEN_TABLE_NAME} AS c,{HEALTH_HISTORY_TABLE_NAME} AS hh
            WHERE c.id = hh.citizen_id
            AND hh.status = 'infected'
            AND DATE(hh.created_at) > DATE(DATE_ADD(NOW(), INTERVAL -2 {unit}));
            '''
        )
    result = cursor.fetchone()
    if result[0] is None:
        return None
    else:
        past_age = result[0]
        percentage_diff = ((current_age-past_age)/past_age) * 100
        return str(round(percentage_diff))
