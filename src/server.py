from flask import Flask
from flask_restful import Resource, Api
from api.bechdel import List_All_Keys, List_Details, Show, Login_User, Logout_User, UserAPI, Register, UpdateRating

app = Flask(__name__)
api = Api(app)

api.add_resource(List_All_Keys, '/list_all_keys')
api.add_resource(List_Details, '/list_details')
api.add_resource(Show, '/show')
api.add_resource(Login_User, '/login')
api.add_resource(Logout_User, '/logout')
api.add_resource(UserAPI, '/user')
api.add_resource(Register, '/register')
api.add_resource(UpdateRating, '/update_rating')


if __name__ == '__main__':
    app.run(debug=True)