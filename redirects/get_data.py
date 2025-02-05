# Script for parsing a list of redirects with endashes and getting data
# about when the page was first edited and by whom

import pywikibot
site = pywikibot.Site('en', 'wikipedia')

import pandas as pd
import numpy as np
import seaborn as sns
import pickle


# This query on Quarry: https://quarry.wmflabs.org/query/17182

"""
select page_id, page_title, rd_title from redirect 
inner join page on rd_from = page_id
where rd_namespace = 0 and rd_title LIKE '%–%'
"""

redirects_df = pd.read_csv("enwiki-redirects-endash-20170308.tsv", sep="\t")
len(redirects_df)

error_count = 0
total_df = pd.DataFrame(columns=["revid",
                                 "timestamp",
                                 "user",
                                 "comment",
                                 "is_redirect",
                                 "page_title",
                                 "page_namespace",
                                 "page_text"])
count = 0 
errors = []

for r in redirects_df.iterrows():
    revs = []
    redirect_page = r[1].page_title
    try:
        page = pywikibot.Page(site, redirect_page)
        oldest_rev = page.oldest_revision
        revs.append((oldest_rev.revid, oldest_rev.timestamp.isoformat(), oldest_rev.user, oldest_rev.comment, page.isRedirectPage(), page.title(), page.namespace().id, page.text))
    except Exception as e:
        errors.append(r[1].page_title)
        error_count = error_count + 1

    rev_df = pd.DataFrame(revs, columns=["revid",
                                         "timestamp",
                                         "user",
                                         "comment",
                                         "is_redirect",
                                         "page_title",
                                         "page_namespace",
                                         "page_text"]) 
    
    total_df = pd.concat([total_df, rev_df])
    
    count = count + 1
    if count % 100 == 0:
        
        total_df.to_csv("enwiki-redirects-endash-processed.tsv", sep="\t")
        total_df.to_pickle("enwiki-redirects-endash-processed.pickle")
        
        with open('enwiki-redirects-endash-errors.pickle', 'wb') as fp:
            pickle.dump(errors, fp)
        
        with open('enwiki-redirects-endash-errors.tsv', 'wb') as ft:
            for item in errors:
                ft.write(bytes(item + "\n", 'UTF-8'))
        
        print(count, error_count)
    
