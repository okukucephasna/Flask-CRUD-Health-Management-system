from flask import Flask, request, render_template, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
import pymysql

app = Flask(__name__)
api = Api(app)
CORS(app)

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="testone"
)
cursor = connection.cursor()

# Serve HTML page
@app.route('/')
def home():
    return render_template('index.html')

# --- Clients Resource ---
class DataResource(Resource):
    def get(self):
        cursor.execute("SELECT * FROM users1")
        result = cursor.fetchall()

        users = []
        for row in result:
            users.append({
                'id': row[0],
                'first_name': row[1],
                'second_name': row[2],
                'job': row[3]
            })

        return {'data': users}

class CreateUserResource(Resource):
    def post(self):
        data = request.get_json()
        first_name = data['first_name']
        second_name = data['second_name']
        job = data['job']

        query = "INSERT INTO users1 (first_name, second_name, job) VALUES (%s, %s, %s)"
        cursor.execute(query, (first_name, second_name, job))
        connection.commit()

        return {'message': 'User created successfully'}

# --- Programs Resource ---
class ProgramResource(Resource):
    def get(self):
        cursor.execute("SELECT * FROM programs")
        result = cursor.fetchall()
        programs = [{'id': row[0], 'program_name': row[1]} for row in result]
        return {'programs': programs}

    def post(self):
        data = request.get_json()
        program_name = data['program_name']

        query = "INSERT INTO programs (program_name) VALUES (%s)"
        cursor.execute(query, (program_name,))
        connection.commit()

        return {'message': 'Program created successfully'}

# --- Enrollment Resource ---
class EnrollmentResource(Resource):
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        program_id = data['program_id']

        query = "INSERT INTO enrollments (user_id, program_id) VALUES (%s, %s)"
        cursor.execute(query, (user_id, program_id))
        connection.commit()

        return {'message': 'Client enrolled successfully'}

# --- Client Profile Resource ---
class ClientProfileResource(Resource):
    def get(self, user_id):
        cursor.execute("SELECT * FROM users1 WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return {'message': 'User not found'}, 404

        cursor.execute("""
            SELECT p.program_name
            FROM enrollments e
            JOIN programs p ON e.program_id = p.id
            WHERE e.user_id = %s
        """, (user_id,))
        programs = cursor.fetchall()
        enrolled_programs = [row[0] for row in programs]

        return {
            'id': user[0],
            'first_name': user[1],
            'second_name': user[2],
            'job': user[3],
            'enrolled_programs': enrolled_programs
        }

# Register resources
api.add_resource(DataResource, '/users')
api.add_resource(CreateUserResource, '/users')
api.add_resource(ProgramResource, '/programs')
api.add_resource(EnrollmentResource, '/enroll')
api.add_resource(ClientProfileResource, '/users/<int:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
