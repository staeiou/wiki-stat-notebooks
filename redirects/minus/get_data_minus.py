# Script for parsing a list of redirects with endashes and getting data
# about when the page was first edited and by whom

import pywikibot
site = pywikibot.Site('en', 'wikipedia')

import pandas as pd
import numpy as np
import seaborn as sns
import pickle


# This query on Quarry: https://quarry.wmflabs.org/query/17222

"""
select page_id, page_title from page where page_namespace = 0 and page_is_redirect = 1 and page_title LIKE '%-%'
"""

redirects_df = pd.read_csv("enwiki-redirect-pages-with-minus-20170309.tsv", sep="\t")
num_redirects = len(redirects_df)

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
    page = pywikibot.Page(site, r[1].page_title)
    try:
        for rev in page.revisions(content=True, reverse=True):
            if rev.text.find("–") >= 0:
                oldest_rev = rev
                break
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
        
        total_df.to_csv("enwiki-redirects-minus-processed.tsv", sep="\t")
        total_df.to_pickle("enwiki-redirects-minus-processed.pickle")
        
        with open('enwiki-redirects-minus-errors.pickle', 'wb') as fp:
            pickle.dump(errors, fp)
        
        with open('enwiki-redirects-minus-errors.tsv', 'wb') as ft:
            for item in errors:
                ft.write(bytes(item + "\n", 'UTF-8'))
        percent = round(((count/num_redirects)*100),4)
        print(str(percent) + "% done\t count: ", count, "\terrors: ", error_count)
    
