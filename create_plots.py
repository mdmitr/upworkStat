from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import operator
#import plot_check
from textwrap import wrap
import pprint
import os.path


def plot_check_files():
    if (os.path.isfile('upwork.db') is False):
        print "Please run query.py to load data from upwork"
        return False

    if (os.path.isfile('skills.txt') is False):
        print '''Please create file skills.txt and fill it
        with skills you interested in'''
        return False

    return True


def autolabel_h(rects):
    for rect in rects:
        width = rect.get_width()
        plt.text(0.5*width, rect.get_y() + rect.get_height()/2,
                 '%d' % int(width), ha='center', va='center')


def get_skills():
    skills = []
    with open('skills.txt') as f:
        skills = f.read().splitlines()
    return skills


def plot_jobs_by_skills(cur, skills):

    skill_jobs = {}
    
    for skill in skills:
        cur.execute('''select count(j.id) amount from jobs j where j.id in
                    (select js.job_id from job_skills js where js.skill=?)''',
                    (skill,))
        res = cur.fetchone()
        skill_jobs[skill] = res[0]
    
    sorted_skill_jobs = zip(*sorted(skill_jobs.items(),
                            key=operator.itemgetter(1), reverse=False))

    fig = plt.figure()
    
    y_pos = np.arange(len(skill_jobs))
    print y_pos
    
    ax = plt.barh(y_pos, sorted_skill_jobs[1], align='center', alpha=0.3)
    plt.yticks(y_pos, ['\n'.join(wrap(x, 10)) for x in sorted_skill_jobs[0]])
    plt.ylabel('Skill')
    plt.xlabel('Amount of jobs')
    autolabel_h(ax)
    
    plt.gcf().subplots_adjust(left=0.20)
    
    return fig


def plot_jobs_by_skills_and_category(cur, skills):

    figs = []

    for skill in skills:
        cur.execute('''
select sum(amount) amount, cat || ' / ' || subcat 
  from (select 1 as amount, cats.cat, cats.subcat
          from jobs j,
               (select distinct category2 cat, subcategory2 subcat
                  from jobs
                 order by cat, subcat) cats
         where j.subcategory2 = subcat
           and j.category2 = cat
           and j.id in (select job_id from job_skills where skill = ?))
 group by cat, subcat
 order by amount desc''',
                    (skill,))
        res = cur.fetchall()


        jobs = zip(*res)

        fig = plt.figure()
        fig.set_size_inches(15,15)
        figs.append(fig)

        labels = ['\n'.join(wrap(x, 50)) for x in jobs[1]]
 
        patches, texts = plt.pie(jobs[0], labels=labels)
        plt.title('Amount of jobs for '+skill)
        # plt.legend(patches, labels, loc=2)
 
    return figs


if __name__ == '__main__':

    if (plot_check_files() is False):
        raise 'EEE'

    skills = get_skills()
       
    con = sqlite3.connect('upwork.db')
    cursor = con.cursor()

    pp = PdfPages('upwork.pdf')

#    plot1 = plot_jobs_by_skills(cursor, skills)
#    pp.savefig(plot1)

    plots2 = plot_jobs_by_skills_and_category(cursor, skills)
    for plot in plots2:
        pp.savefig(plot)
    pp.close()

    con.close()
#    plt.show()











