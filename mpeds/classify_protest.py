
import glob
import sys
import urllib
import urllib2

import json

import pandas as pd 
import numpy as np

from sklearn.externals import joblib

class MPEDS:
    def __init__(self):
        ''' Constructor. '''
        self.search_str  = 'boycott* "press conference" "news conference" (protest* AND NOT protestant*) strik* rally ralli* riot* sit-in occupation mobiliz* blockage demonstrat* marchi* marche*'
        self.solr_url    = None

        self.hay_clf     = None
        self.hay_vect    = None
        self.form_clf    = None
        self.form_vect   = None
        self.issue_clf   = None
        self.issue_vect  = None
        self.target_clf  = None
        self.target_vect = None


    def setSolrURL(self, url):
        self.solr_url = url


    def buildSolrQuery(self, q_dict):
        ''' Build a query for a Solr request. '''
        q = []
        for k, v in q_dict.iteritems():
            sub_q = '%s:"%s"' % (k, v)
            q.append(sub_q)

        query = ' AND '.join(q)
        return query


    def makeSolrRequest(self, q, fq, protest = False):
        """ makes Solr requests to get article texts """

        data = {
            'q':     q,
            'start': start,
            'rows':  rows,
            'wt':    'json'
        } 

        ## put protest string into fq field
        if protest:
            data['fq'] = self.search_str

        data = urllib.urlencode(data)
        req  = urllib2.Request(solr_url, data)
        res  = urllib2.urlopen(req)
        res  = json.loads(res.read())

        numFound = res['response']['numFound']

        print("%d documents found." % numFound)

        ## add 100 to get everything for sure
        numFound += 100

        articles = []
        interval = 100
        prev = 0
        for i in range(0, numFound, interval):
            data = {
                'q': q,
                'fq': fq,
                'rows': interval,
                'start': prev,
                'wt': 'json'
            }
            data = urllib.urlencode(data)
            req  = urllib2.Request(url, data_str)
            res  = urllib2.urlopen(req)
            res  = json.loads(res.read())

            articles.extend(res['response']['docs'])

            if i % 1000 == 0:
                print('%d documents collected.' % i)

            prev = i

        return docs


    def getLede(self, text):
        ''' Get the lede sentence for this text. '''
        sentences = text.split("<br/>")
        return sentences[0]

    def haystack(self, text):
        ''' '''

        ## load vectorizer
        if not self.hay_vect:
            print('Loading vectorizer...')
            self.hay_vect = joblib.load('classifiers/haystack-vect_all-source_2016-03-21.pkl')

        print('Vectorizing...')
        X = self.hay_vect.transform(text)

        ## load classifier
        if not self.hay_clf:          
            print('Loading classifier...')
            self.hay_clf = joblib.load('classifiers/haystack_all-source_2016-03-21.pkl')

        print('Predicting...')
        y = self.hay_clf.predict(X)
        return y


    def getForm(self, text):
        ''' '''
        if not self.form_vect:
            print('Loading form vectorizer...')
            self.form_vect = joblib.load('classifiers/form-vect_2017-05-23.pkl')

        print('Vectorizing...')
        X = self.form_vect.transform(text)

        ## load classifier
        if not self.form_clf:          
            print('Loading form classifier...')
            self.form_clf = joblib.load('classifiers/form_2017-05-23.pkl')

        print('Predicting...')
        y = self.form_clf.predict(X)
        return y


    def getFormProb(self, text):
        ''' '''
        if not self.form_vect:
            print('Loading form vectorizer...')
            self.form_vect = joblib.load('classifiers/form-vect_2016-04-28.pkl')

        print('Vectorizing...')
        X = self.form_vect.transform(text)

        ## load classifier
        if not self.form_clf:
            print('Loading form classifier...')
            self.form_clf = joblib.load('classifiers/form_2016-04-28.pkl')

        print('Predicting form probabilities...')
        probs    = self.form_clf.predict_proba(X)
        p_tuples = []
        for i in range(0, self.form_clf.classes_.shape[0]):
            p_tuples.append( (self.form_clf.classes_[i], probs[i]) )

        return p_tuples


    def getIssue(self, X):
        ''' '''
        pass

    def getIssueProb(self, X):
        ''' '''
        pass


    def getTarget(self, X):
        ''' '''
        pass

    def getTargetProb(self, X):
        ''' '''
        pass


    def getLocation(self, document):
        pass


    def getSMO(self, document):
        pass


    def getSize(self, document):
        pass
