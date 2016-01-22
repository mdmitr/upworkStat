import sqlite3


def create_job_tables(cur):

    #
    # JOBS
    #

    cur.execute('DROP TABLE IF EXISTS JOBS')

    cur.execute('''CREATE TABLE JOBS (id VARCHAR(50) PRIMARY KEY,
     title VARCHAR(500), category2 VARCHAR(50), subcategory2 VARCHAR(50),
     job_status VARCHAR(50), job_type VARCHAR(50),
     snippet VARCHAR(2048), url VARCHAR(128), workload VARCHAR(100),
     budget INTEGER, date_created DATETIME)''')

    #
    # JOB SKILLS
    #

    cur.execute('DROP TABLE IF EXISTS JOB_SKILLS')

    cur.execute('''CREATE TABLE JOB_SKILLS (job_id VARCHAR(50), skill VARCHAR(50),
       FOREIGN KEY(job_id) REFERENCES JOBS(id),
       UNIQUE(job_id, skill) ON CONFLICT REPLACE)''')

    cur.execute('CREATE INDEX JOB_SKILLS_IDX1 ON JOB_SKILLS(skill)')


def create_fl_tables(cur):
    #
    # FLS
    #

    cur.execute('DROP TABLE IF EXISTS FLS')

    cur.execute('''CREATE TABLE FLS (id VARCHAR(50) PRIMARY KEY,
     country VARCHAR(100),
     description VARCHAR(2048),
     feedback REAL,
     last_activity DATETIME, member_since DATETIME,
     name VARCHAR(500),
     portfolio_items_count INTEGER,
     rate REAL,
     test_passed_count INTEGER,
     title VARCHAR(500))''')

    #
    # FL SKILLS
    #

    cur.execute('DROP TABLE IF EXISTS FL_SKILLS')

    cur.execute('''CREATE TABLE FL_SKILLS (fl_id VARCHAR(50), skill VARCHAR(50),
       FOREIGN KEY(fl_id) REFERENCES FLS(id),
       UNIQUE(fl_id, skill) ON CONFLICT REPLACE)''')

    cur.execute('''CREATE INDEX FL_SKILLS_IDX1 ON FL_SKILLS(skill)''')

    #
    # FL CATS
    #

    cur.execute('DROP TABLE IF EXISTS FL_CATS')

    cur.execute('''CREATE TABLE FL_CATS (fl_id VARCHAR(50), category VARCHAR(50),
       FOREIGN KEY(fl_id) REFERENCES FLS(id),
       UNIQUE(fl_id, category) ON CONFLICT REPLACE)''')

    cur.execute('CREATE INDEX FL_CATS_IDX1 ON FL_CATS(category)')

    #
    # FLS CATS2
    #

    cur.execute('DROP TABLE IF EXISTS FL_CATS2')

    cur.execute('''CREATE TABLE FL_CATS2 (fl_id VARCHAR(50), category2 VARCHAR(50),
       FOREIGN KEY(fl_id) REFERENCES FLS(id),
       UNIQUE(fl_id, category2) ON CONFLICT REPLACE)''')

    cur.execute('CREATE INDEX FL_CATS2_IDX1 ON FL_CATS2(category2)')

if __name__ == '__main__':

    con = sqlite3.connect('upwork.db')
    cur = con.cursor()

    create_job_tables(cur)
    create_fl_tables(cur)

    con.commit()
    con.close()
