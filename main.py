from flask import Flask
from flask_restful import Resource, Api
from flask_restful import  reqparse

app = Flask(__name__)
api = Api(app)

class RegistUser(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        args = parser.parse_args()

        name = args['name']
        email = args['email']

        print(name)
        print(email)

        return {'result':'ok'}

class Write(Resource):
    def post(self):

        return {'result' : '오키키'}

api.add_resource(RegistUser, '/user')
api.add_resource(Write, '/write')

@app.route('/write')
def hello_world():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
