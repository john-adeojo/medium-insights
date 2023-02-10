"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.4
"""

# Imports 

import datetime
import json 
import requests
import pandas as pd
import itertools 
from datetime import datetime, timedelta, date


def request_data(parameters: dict):
    
    #start_date = requested_date_range.start_date.astype(str)
    #end_date = requested_date_range.end_date.astype(str)
    start_date = parameters["start_date"]
    end_date = parameters["end_date"]
    
    def remove_none(lst):
        return [x for x in lst if x is not None]

    def count_unique(lst):
        return len(set(lst))

    def count_unique_dicts(lst_of_dicts):
        return len(set(tuple(sorted(d.items())) for d in lst_of_dicts))

    def remove_duplicates(lst):
        return list(set(lst))
    
    def generate_query_strings(start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query_strings = []
        current_date = start_date
        while current_date <= end_date:
            query_string = {"from": current_date.strftime("%Y-%m-%dT%H:%M:%S")}
            query_strings.append(query_string)
            current_date += timedelta(days=1)
        return query_strings

    query_string_list = generate_query_strings(start_date=start_date, end_date=start_date)

    print("total count list:", len(query_string_list))
    print("date pull requests", query_string_list)
    print("unique count list:", count_unique_dicts(query_string_list))
    
    # Make API calls and format data
    # Request article IDs from specified publications limited at 25 per request

    article_ids = []
    for query in query_string_list:

        url = "https://medium2.p.rapidapi.com/publication/7f60cf5620c9/articles"

        querystring = query

        headers = {
            "X-RapidAPI-Key": "154b04f735msh95207f233e150b4p160e64jsnbede5ac2c0cc",
            "X-RapidAPI-Host": "medium2.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        response_dict = json.loads(response.text).get('publication_articles')
        article_ids.append(response_dict)
        
    article_ids_clean = remove_none(article_ids)

    # Flatten list
    article_list = list(itertools.chain(*article_ids_clean))

    print("total count list:", len(article_list))
    print("unique count list:", count_unique(article_list))

    article_list = remove_duplicates(article_list)

    print("de-duped:")

    print("total count list:", len(article_list))
    print("unique count list:", count_unique(article_list))
    
    # Request article meta data 
    article_data = []
    for article in article_list:
        url = "https://medium2.p.rapidapi.com/article/" + article

        headers = {
            "X-RapidAPI-Key": "154b04f735msh95207f233e150b4p160e64jsnbede5ac2c0cc",
            "X-RapidAPI-Host": "medium2.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)
        response_dict = json.loads(response.text)
        article_data.append(response_dict)
        
    df = pd.DataFrame(article_data)
        
    author_list = df.author.values

    print("total count list:", len(author_list))
    print("unique count list:", count_unique(author_list))

    author_list = remove_duplicates(author_list)

    print("total count list:", len(author_list))
    print("unique count list:", count_unique(author_list))

    author_list = [item for item in author_list if item == item]
    
    # Author info

    author_data = []

    for author_id in author_list:

        url = "https://medium2.p.rapidapi.com/user/" +  author_id

        headers = {
            "X-RapidAPI-Key": "154b04f735msh95207f233e150b4p160e64jsnbede5ac2c0cc",
            "X-RapidAPI-Host": "medium2.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)
        response_dict = json.loads(response.text)
        author_data.append(response_dict)
        
    author_df = pd.DataFrame(author_data)
    author_df.rename(columns={"id": "Author ID"}, inplace=True)
    
    # Article content
    article_content = []
    for article in article_list:
        url = "https://medium2.p.rapidapi.com/article/" + article + "/content"

        headers = {
            "X-RapidAPI-Key": "154b04f735msh95207f233e150b4p160e64jsnbede5ac2c0cc",
            "X-RapidAPI-Host": "medium2.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)
        response_dict = json.loads(response.text)
        response_dict.update([('Article ID', article)])

        article_content.append(response_dict)
        
    # Create table
    article_metadata_df = df
    article_metadata_df.rename(columns={"id": "Article ID", "author": "Author ID"}, inplace=True)

    # Author: Add follower Count 
    author_df = pd.DataFrame(author_data)
    author_df.rename(columns={"id": "Author ID"}, inplace=True)

    # Merge 
    analysis_df = article_metadata_df.merge(author_df, how="left", left_on="Author ID", right_on="Author ID")
    analysis_df["Follower Adjusted Claps"] = analysis_df["claps"] /analysis_df["followers_count"]

    data_request_date = date.today()
    
    data_request_date = pd.DataFrame({'data_request_date': [data_request_date]})
    
    #print("Data request date", data_request_date)

    
    return analysis_df, article_content, data_request_date

 

        
        

  
    

