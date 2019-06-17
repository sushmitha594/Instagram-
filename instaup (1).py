# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 10:57:21 2018

@author: sunny
"""

import json
import requests
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
from googletrans import Translator

tag = 'africa'
url = 'https://www.instagram.com/explore/tags/'+tag.lower()+'/?__a=1'

keys =['id','owner','src','shortcode','edge_media_to_caption','edge_media_to_comment','edge_liked_by']


def get_ig_page(url, session=None):
    print(url)
    session = session or requests.Session()
    
    r = session.get(url)
    r_code = r.status_code
    
    if r_code == requests.codes.ok:
        # the code is 200 or valid
        return r
    else:
        return None

  
ig_data_dict = get_ig_page(url)

if ig_data_dict is not None:
   
    ig_data_dict = ig_data_dict.json()

    data = ig_data_dict.get('graphql',None)
    hashtagData = data.get('hashtag',None)
    
    top_posts_dict={}
    top_posts = hashtagData.get('edge_hashtag_to_top_posts',None)
    if top_posts is not None:
        top_posts_edges = top_posts.get('edges')
        for i,arr in enumerate(top_posts_edges):           
            top_posts_dict[i] = (arr.get('node'))

        timestamp = {}
        popular_hashtags=[]
        popular_hashtags_translated=[]
        post_text = []
        for index,key in enumerate(top_posts_dict.items()):
            top_posts_nodes_captions = key[1]['edge_media_to_caption']
            timestamp[index] = key[1]['taken_at_timestamp']
            top_posts_nodes_edges =  top_posts_nodes_captions['edges']
            if len(top_posts_nodes_edges) > 0:
                top_posts_nodes_text = top_posts_nodes_edges[0].get('node').get('text').split(' ')           
                top_posts_text = ' '.join(top_posts_nodes_text)
                popular_hashtags.append(re.findall(r"(?<=#)\w+", top_posts_text))                     
            
        translator = Translator()
        translated = translator.translate(popular_hashtags, dest = 'en')
        for post in translated :
            for hashtag in post:
                popular_hashtags_translated.append(hashtag.text)
        
        tm_dict = {}
        tm_dict['AM'] = 0
        tm_dict['PM'] = 0

        top_posts_year = {}
        top_posts_local_time = {}
        top_posts_hour = {}
        for each_time in timestamp.items():
            top_posts_time = datetime.fromtimestamp(each_time[1]).strftime('%Y-%m-%d %H:%M:%S')
            top_posts_year = top_posts_time.split()[0].split('-')[0]
            top_posted_time = datetime.fromtimestamp(each_time[1]).strftime("%I:%M:%S %p")
            top_posts_hour = top_posted_time.split()[0].split(':')[0]
            top_posts_local_time = top_posted_time.split()[1]
            if top_posts_local_time == 'AM':
                tm_dict['AM']+=1
            elif top_posts_local_time == 'PM':
                tm_dict['PM']+=1

        X = tm_dict.keys()
        Y = tm_dict.values()
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0]=8
        fig_size[1]=5
        plt.rcParams["figure.figsize"]=fig_size
        plt.bar(range(len(X)), Y, color='g', alpha=1, edgecolor='black')
        plt.xlabel('Time posted')
        plt.ylabel('Posts')
        plt.xticks(range(len(X)), X)  
        plt.tight_layout()
        plt.show() 

        all_posts_dict={}
        all_posts = hashtagData.get('edge_hashtag_to_media',None)
        if all_posts is not None:
            all_posts_edges = all_posts.get('edges')
            for i,arr in enumerate(all_posts_edges):           
                all_posts_dict[i] = (arr.get('node'))
    
            all_posts_timestamp = {}
            all_posts_like_count = {}
            for index,key in enumerate(all_posts_dict.items()):
                all_posts_like_count[index] = key[1]['edge_liked_by']['count']
                all_posts_timestamp[index] = key[1]['taken_at_timestamp']
                
                        
        all_posts_time_period= ["AM", "PM"]
        all_posts_year = {}
        all_posts_local_time = {}
        all_posts_hour = {}
        all_tm_dict = {}
        for each_time in all_posts_timestamp.items():
            all_posts_time = datetime.fromtimestamp(each_time[1]).strftime('%Y-%m-%d %H:%M:%S')
            all_posts_year = all_posts_time.split()[0].split('-')[0]
            all_posted_time = datetime.fromtimestamp(each_time[1]).strftime("%I:%M:%S %p")
            all_posts_hour = all_posted_time.split()[0].split(':')[0]
            all_posts_local_time = all_posted_time.split()[1]
            all_tm_dict[str(each_time[0])]=str(all_posts_local_time)

            
        fig, ax1 = plt.subplots()       
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0]=25
        fig_size[1]=5
        plt.rcParams["figure.figsize"]=fig_size

        color = 'tab:blue'
        ax1.set_xlabel('Posts')
        ax1.set_ylabel('Like count', color=color)
        ax1.bar(range(len(all_posts_like_count.keys())), all_posts_like_count.values(), color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        
        color = 'tab:red'
        ax2.set_ylabel('Time posted', color=color) 
        ax2.plot(range(len(all_tm_dict.keys())), all_tm_dict.values(), color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        plt.yticks([0, 1], all_posts_time_period)
        fig.tight_layout() 
        plt.show()
        
        dx = all_tm_dict.values()
        x = range(len(all_tm_dict.keys()))
        y = all_tm_dict.values()
        plt.show()
                          
        def show_wordcloud(data):
            wordcloud = WordCloud(
                    background_color='white',
                    max_words=200,
                    max_font_size=40, 
                    random_state=42
                    ).generate(str(data))

            fig = plt.figure(1)
            plt.imshow(wordcloud)
            plt.axis('off')
            plt.show()
            fig.savefig("word1.png", dpi=900)    
        show_wordcloud(popular_hashtags_translated)


else:
    print('Something is wrong')
