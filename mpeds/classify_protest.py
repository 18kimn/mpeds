
import glob
import sys
import urllib
import urllib2

import json

import pandas as pd
import numpy as np

from sklearn.externals import joblib
from mpeds.open_ended_coders import *

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

        self.size_clf = None
        self.location_clf = None
        self.smo_clf = None


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


    def makeSolrRequest(self, q, fq = None, protest = False):
        """ makes Solr requests to get article texts """

        data = {
            'q':     q,
            'start': 0,
            'rows':  10,
            'wt':    'json'
        }

        ## put protest string into fq field
        if protest:
            data['fq'] = self.search_str

        data = urllib.urlencode(data)
        req  = urllib2.Request(self.solr_url, data)
        res  = urllib2.urlopen(req)
        res  = json.loads(res.read())

        numFound = res['response']['numFound']

        print("%d documents found." % numFound)

        interval = 100

        ## add 100 to get everything for sure
        numFound += interval

        prev = 0
        data = {
            'q': q,
            'rows': interval,
            'start': prev,
            'wt': 'json'
        }

        if fq and not protest:
            data['fq'] = fq

        articles = []
        for i in range(0, numFound, interval):
            data = {
                'q': q,
                'rows': interval,
                'start': prev,
                'wt': 'json'
            }

            data = urllib.urlencode(data)
            req  = urllib2.Request(self.solr_url, data)
            res  = urllib2.urlopen(req)
            res  = json.loads(res.read())

            articles.extend(res['response']['docs'])

            if i % 1000 == 0:
                print('%d documents collected.' % i)

            prev = i

        return articles


    def getLede(self, text):
        ''' Get the lede sentence for this text. '''
        sentences = text.split("<br/>")
        return sentences[0]

    def haystack(self, text):
        '''
        Perform haystack classification task.

        :param text: documents to be classified
        :type text: pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''

        ## load vectorizer
        if not self.hay_vect:
            print('Loading vectorizer...')
            self.hay_vect = joblib.load('classifiers/haystack-vect_all-source_2017-05-24.pkl')

        print('Vectorizing...')
        X = self.hay_vect.transform(text)

        ## load classifier
        if not self.hay_clf:
            print('Loading classifier...')
            self.hay_clf = joblib.load('classifiers/haystack_all-source_2017-05-24.pkl')

        print('Predicting...')
        y = self.hay_clf.predict(X)
        return y


    def getForm(self, text):
        '''
        Classify protest form.

        :param text: documents to perform classification task on
        :type text: pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''

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
            self.form_vect = joblib.load('classifiers/form-vect_2017-05-23.pkl')

        print('Vectorizing...')
        X = self.form_vect.transform(text)

        ## load classifier
        if not self.form_clf:
            print('Loading form classifier...')
            self.form_clf = joblib.load('classifiers/form_2017-05-23.pkl')

        print('Predicting form probabilities...')
        probs    = self.form_clf.predict_proba(X)
        p_tuples = []
        for i in range(0, self.form_clf.classes_.shape[0]):
            p_tuples.append( (self.form_clf.classes_[i], probs[i]) )

        return p_tuples


    def getIssue(self, text):
        '''
        Classify protest issue.

        :param text: documents to perform classification task on
        :type text: pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''

        if not self.issue_vect:
            print('Loading issue vectorizer...')
            self.issue_vect = joblib.load('classifiers/issue-vect_2017-05-23.pkl')

        print('Vectorizing...')
        X = self.issue_vect.transform(text)

        ## load classifier
        if not self.issue_clf:
            print('Loading issue classifier...')
            self.issue_clf = joblib.load('classifiers/issue_2017-05-23.pkl')

        print('Predicting...')
        y = self.issue_clf.predict(X)

        return y

    def getIssueProb(self, text):
        ''' '''

        # SGDclassifiers with loss='hinge' are linear SVMs, and thus do not support probability estimates
        print('Sorry, issue classification model does not support probability estimates')


    def getTarget(self, text):
        '''
        Classify protest target.

        :param text: documents to perform classification task on
        :type text: pandas series of strings

        :return: predictions
        :rtype: pandas series
        '''
        if not self.target_vect:
            print('Loading target vectorizer...')
            self.target_vect = joblib.load('classifiers/target-vect_2017-05-23.pkl')

        print('Vectorizing...')
        X = self.target_vect.transform(text)

        ## load classifier
        if not self.target_clf:
            print('Loading target classifier...')
            self.target_clf = joblib.load('classifiers/target_2017-05-23.pkl')

        print('Predicting...')
        y = self.target_clf.predict(X)

        return y

    def getTargetProb(self, text):
        ''' '''

        print('Sorry, target classification model does not support probability estimates')



    def getSMO(self, text):
        '''
        Extract social movement organizations from text

        :param text: documents to perform coding task on
        :type text: pandas series of strings

        :return: extracted SMOs
        :rtype: pandas series
        '''

        if not self.smo_clf:
            self.smo_clf = SMOCoder()

        SMOs = text.apply(self.smo_clf.getSMO, args = [True])

        return SMOs

    def getSize(self, text):
        '''
        Extract protest from text

        :param text: documents to perform coding task on
        :type text: pandas series of strings

        :return: extracted sizes
        :rtype: pandas series
        '''
        if not self.size_clf:
            self.size_clf = SizeCoder()

        sizes = text.apply(self.size_clf.getSize, args = [True])

        return sizes

    def getLocation(self, text):
        '''
        Extract locations from text

        :param text: documents to perform coding task on
        :type text: pandas series of strings

        :return: extracted locations
        :rtype: pandas series
        '''

        if not self.location_clf:
            self.location_clf = LocationCoder()

        locations = text.apply(self.location_clf.getLocation)

        return locations
