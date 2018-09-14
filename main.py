import os

from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials

import jinja2
import webapp2

#AutoML
from google.cloud import automl_v1beta1

#from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True,
                               extensions=['jinja2.ext.autoescape'])

PROJECT = 'machine-learning-crowdsourcing'
params={}
response={}

def get_prediction(content, project_id, model_id):
    prediction_client = automl_v1beta1.PredictionServiceClient()
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'text_snippet': {'content': content, 'mime_type': 'text/plain'}}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request  # waits till request is returned

class BaseHandler(webapp2.RequestHandler):
    def render_template(self, template, params):
#        user = users.get_current_user()
#        if user:
#            url = users.create_logout_url(self.request.uri)
#            url_linktext = 'Logout'
#        else:
#            url = users.create_login_url(self.request.uri)
#            url_linktext = 'Login'
#        params = {'user': user,
#                  'url': url,
#                  'url_linktext': url_linktext}
        self.response.out.write(jinja_env.get_template(template).render(params))


class MainHandler(BaseHandler):
    def get(self):
        self.render_template('main.html',params={})

class Api1Handler(BaseHandler):
    def get(self):
        self.render_template('api1.html', params={})

    def post(self):
        submit = self.request.get('submit')
        response = {}
        if submit == 'request':
            vendor = self.request.get('vendor')
            MODEL = 'merch_cat'
            VERSION = 'v2'

            try:
                credentials = GoogleCredentials.get_application_default()
                api = discovery.build('ml', 'v1', credentials=credentials)
                request_data = {"instances": [{"inputs": vendor}]}

                parent = 'projects/%s/models/%s/versions/%s' % (PROJECT, MODEL, VERSION)
                response = api.projects().predict(body=request_data, name=parent).execute()
                print "response={0}".format(response)

            except errors.HttpError, err:
                print(err._get_reason())

            self.render_template('api1_response.html', params=response)

class Api2Handler(BaseHandler):
    def get(self):
        params = { "sepal_length": 5.9,
                   "sepal_width": 2.5,
                   "petal_length": 4.5,
                   "petal_width": 1.7 }
        self.render_template('api2.html', params=params)

    def post(self):
        submit = self.request.get('submit')
        response = {}
        if submit == 'request':
            sepal_length = self.request.get('sepal_length')
            sepal_width = self.request.get('sepal_width')
            petal_length = self.request.get('petal_length')
            petal_width = self.request.get('petal_width')
            MODEL = 'TFIRIS'
            VERSION = 'v1'

            try:
                credentials = GoogleCredentials.get_application_default()
                api = discovery.build('ml', 'v1', credentials=credentials)
                request_data = {"instances": [{"csv_line": ', '.join(["120", sepal_length, sepal_width, petal_length, petal_width]) }]}

                parent = 'projects/%s/models/%s/versions/%s' % (PROJECT, MODEL, VERSION)
                response = api.projects().predict(body=request_data, name=parent).execute()
                print "response={0}".format(response)

            except errors.HttpError, err:
                print(err._get_reason())

            self.render_template('api2_response.html', params=response)

class Api3Handler(BaseHandler):


    def get(self):
        params = { "model_id": "TCN5152740728583529794" }
        self.render_template('api3.html', params=params)

    def post(self):
        submit = self.request.get('submit')
        if submit == 'request':
            model_id = self.request.get('model_id')
            description = self.request.get('description')
            response = get_prediction(description, PROJECT,  model_id)

            self.render_template('api3_response.html', params=response)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/api1', Api1Handler),
    ('/api2', Api2Handler),
    ('/api3', Api3Handler),
], debug=True)