
import sqlite3
import dateutil.parser
import time
import os.path
from tqdm import tqdm

from keys import public_key, secret_key

path = os.path.dirname(os.path.abspath(__file__))
os.environ['HTTPLIB_CA_CERTS_PATH'] = 'cacerts.txt'

import upwork

def desktop_app():
    """Emulation of desktop app.
    Your keys should be created with project type "Desktop".

    Returns: ``upwork.Client`` instance ready to work.

    """
    print 'Emulating desktop app'

    client = upwork.Client(public_key, secret_key)
    auth_url = client.auth.get_authorize_url()

    verifier = raw_input(
        'Please enter the verification code you get '
        'following this link:\n{0}\n\n> '.format(
            auth_url))

    print 'Retrieving keys.... '
    access_token, access_token_secret = client.auth.get_access_token(verifier)
    print 'OK'

    # For further use you can store ``access_toket`` and
    # ``access_token_secret`` somewhere
    client = upwork.Client(public_key, secret_key,
                           oauth_access_token=access_token,
                           oauth_access_token_secret=access_token_secret)
    return client


def query_jobs(client, query):
    all_jobs = []
    offset = 0
    retry = 0

    while True:
        try:
            jobs = client.provider_v2.search_jobs(data=query,
                                                  page_offset=offset,
                                                  page_size=100)
        except Exception as e:
            print 'Error, trying again'
            time.sleep(5)
            retry = retry + 1
            if (retry > 10):
                raise e
            continue

        all_jobs.extend(jobs)
        if (len(jobs) < 100):
            break
        offset = offset + 100
        retry = 0
        print(offset)

    return all_jobs


def save_jobs(con, jobs):

    data_jobs = []
    data_skills = []
    ids = set()

    cur = con.cursor()

    for job in jobs:

        if (job['id'] in ids):
            continue
        ids.add(job['id'])

        cur.execute('select id from JOBS where id=?', (job['id'], ))
        res = cur.fetchone()
        if (res is not None):
            continue

        data_jobs.append((job['id'],
                          job['title'],
                          job['category2'],
                          job['subcategory2'],
                          job['job_status'],
                          job['job_type'],
                          job['snippet'],
                          job['url'],
                          job['workload'],
                          job['budget'],
                          dateutil.parser.parse(job['date_created'])))

        for skill in job['skills']:
            data_skills.append((job['id'], skill))

    print 'saving ', len(data_jobs), 'jobs'

    cur.executemany('''insert into JOBS(id, title, category2, subcategory2,
                                        job_status, job_type, snippet, url,
                                        workload, budget, date_created)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    data_jobs)

    cur.executemany('''insert into JOB_SKILLS(job_id, skill) VALUES(?, ?)''',
                    data_skills)

    con.commit()


def query_all_jobs(client, con, skills):

    for skill in skills:
        # query = { 'skills': skill, 'days_posted' : 356 }
        query = {'skills': skill}
        print 'Querying for skill', skill
        jobs = query_jobs(client, query)
        print len(jobs), 'jobs found'
        save_jobs(con, jobs)


def save_fls(con, fls):

    data_fls = []
    data_skills = []
    data_cats = []
    data_cats2 = []
    ids = set()

    cur = con.cursor()

    for fl in fls:

        if (fl['id'] in ids):
            continue
        ids.add(fl['id'])

        cur.execute('select id from FLS where id=?', (fl['id'], ))
        res = cur.fetchone()
        if (res is not None):
            continue

        data_fls.append((fl['id'],
                         fl.get('country', None),
                         fl.get('description', None),
                         fl['feedback'],
                         dateutil.parser.parse(fl.get('last_activity',
                                                      '1900-01-01')),
                         dateutil.parser.parse(fl.get('member_since',
                                                      '1900-01-01')),
                         fl['name'],
                         fl.get('portfolio_items_count', 0),
                         fl['rate'],
                         fl.get('test_passed_count', 0),
                         fl.get('title', None)))

        for skill in fl['skills']:
            data_skills.append((fl['id'], skill))

        if ('categories' in fl):
            for cat in fl['categories']:
                data_cats.append((fl['id'], cat))

        if ('categories2' in fl):
            for cat2 in fl['categories2']:
                data_cats2.append((fl['id'], cat2))

    cur.executemany('''insert into FLS(id, country, description, feedback,
                                       last_activity, member_since, name,
                                       portfolio_items_count, rate,
                                       test_passed_count, title)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    data_fls)

    cur.executemany('insert into FL_SKILLS(fl_id, skill) VALUES(?, ?)',
                    data_skills)
    cur.executemany('insert into FL_CATS(fl_id, category) VALUES(?, ?)',
                    data_cats)
    cur.executemany('insert into FL_CATS2(fl_id, category2) VALUES(?, ?)',
                    data_cats2)

    con.commit()


def query_fls(client, query):

    all_fls = []
    offset = 0
    retry = 0

    while True:
        try:
            fls = client.provider_v2.search_providers(data=query,
                                                      page_offset=offset,
                                                      page_size=100)
        except Exception as e:
            print 'Error, trying again'
            time.sleep(5)
            retry = retry + 1
            if (retry > 10):
                raise e
            continue

        all_fls.extend(fls)
        if (len(fls) < 100):
            break
        offset = offset + 100
        retry = 0
        print offset

    return all_fls


def query_all_fls(client, con, skills):

    for skill in skills:
        print "Querying freelancers for skill", skill
        query = {'skills': skill, 'feedback': '[1 TO 5]'}
        fls = query_fls(client, query)
        print len(fls), 'freelancers found for skill', skill
        save_fls(con, fls)



if __name__ == '__main__':



    client = desktop_app()
    con = sqlite3.connect('upwork.db')

    if (os.path.isfile('skills.txt')):
        with open('skills.txt') as f:
            skills = f.read().splitlines()
    else:
        skills = client.provider.get_skills_metadata()

    query_all_jobs(client, con, skills)
    query_all_fls(client, con, skills)

    con.close()
