import pandas as pd
editors = pd.read_csv('user_reg_with_userpages_100k.tsv', delimiter='\t', infer_datetime_format=True)

from datetime import date

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

from datetime import datetime
for index, row in editors.iterrows():
    user_registration = row['user_registration']
    reg_dt = datetime.strptime(str(user_registration), "%Y%m%d%H%M%S")

    oneyr = add_years(reg_dt, 1)
    twoyr = add_years(reg_dt, 2)
    year_mo = reg_dt.strftime("%Y-%m")
    
    query = """sql enwiki "   """
    query += "select " + str(row['user_id']) + " as user_id, " + str(row['user_registration']) + " as user_registration,"
    query += "'" + str(year_mo) + "' as year_mo, "
    query += """count(rev_id) as survival_1yr from ( select rev_id from revision_userindex where rev_user = """ + str(row['user_id'])
    query += " and rev_timestamp BETWEEN " + oneyr.strftime("%Y%m%d%H%M%S") 
    query += " and " + twoyr.strftime("%Y%m%d%H%M%S") + " limit 1 ) as s"
    query += """ " >> /home/staeiou/wiki-stat-notebooks/retention_20180712/query/retention_100k.tsv  """ 
    print(query)
    

