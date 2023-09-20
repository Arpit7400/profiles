from flask import Flask, jsonify, request, session
from pymongo import  errors
import os
import re
import hashlib
from bson import ObjectId
from flask_pymongo import PyMongo
from werkzeug .security import generate_password_hash,check_password_hash


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

# initializing Database
app.config["MONGO_URI"] = "mongodb://localhost:27017/Students"
mongo_s = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Parents'
mongo_p = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Teachers'
mongo_t = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Managements'
mongo_m = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Quizes'
mongo_q = PyMongo(app)

UPLOAD_FOLDER = 'static'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}  # Allowed file extensions for images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create unique indexes for user_id, personal_info.contact.phone, and personal_info.contact.email
mongo_s.db.student_profile.create_index([("user_id", 1)], unique=True)
mongo_s.db.student_profile.create_index([("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})
mongo_s.db.student_profile.create_index([("personal_info.contact.email", 1)], unique=True, partialFilterExpression={"personal_info.contact.email": {"$exists": True}})

mongo_p.db.parent_profile.create_index([("user_id", 1)], unique=True)
mongo_p.db.parent_profile.create_index([("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})
mongo_p.db.parent_profile.create_index([("personal_info.contact.email", 1)], unique=True, partialFilterExpression={"personal_info.contact.email": {"$exists": True}})

mongo_t.db.teacher_profile.create_index([("user_id", 1)], unique=True)
mongo_t.db.teacher_profile.create_index([("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})
mongo_t.db.teacher_profile.create_index([("personal_info.contact.email", 1)], unique=True, partialFilterExpression={"personal_info.contact.email": {"$exists": True}})

mongo_m.db.management_profile.create_index([("user_id", 1)], unique=True)
mongo_m.db.management_profile.create_index([("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})
mongo_m.db.management_profile.create_index([("personal_info.contact.email", 1)], unique=True, partialFilterExpression={"personal_info.contact.email": {"$exists": True}})




# Student Profile 

# functions to support API's
def is_student_user_id_unique(user_id):
    user = get_student(user_id)
    return user

def get_student(user_id):
    user = mongo_s.db.student_profile.find_one({'user_id': user_id})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to a string
    return jsonify(user)

def search_by_mobile_number(number):
    query = {
        "personal_info.contact.phone": number
    }
    matching_documents = mongo_s.db.student_profile.find(query)
    if matching_documents:
        result = [document for document in matching_documents]
        return result
    query = {
        'profile.contact.phone': number
    }
    matching_documents = mongo_t.db.teacher_profile.find(query)
    if matching_documents: 
        result = [document for document in matching_documents]
        return result
    query = {
        "personal_info.contact.parent_phone": number
    }
    matching_documents = mongo_p.db.parent_profile.find(query)
    if matching_documents:
        result = [document for document in matching_documents]
        return result

def search_by_email(email):
    query = {
        "personal_info.contact.email": email
    }
    matching_documents = mongo_s.db.student_profile.find(query)
    if matching_documents:
        result = [document for document in matching_documents]
        return result
    query = {
        'profile.contact.email': email
    }
    matching_documents = mongo_t.db.teacher_profile.find(query)
    if matching_documents:
        result = [document for document in matching_documents]
        return result
    query = {
        "personal_info.contact.parent_email": email
    }
    matching_documents = mongo_p.db.parent_profile.find(query)
    if matching_documents:
        result = [document for document in matching_documents]
        return result

def search_by_username_or_user_id(user):
    result = []
    user_id_query = {
        "user_id": user
    }
    user_id_matching_documents = mongo_s.db.student_profile.find(user_id_query)
    result.extend(user_id_matching_documents)
    username_query = {
        "username": user
    }
    username_matching_documents = mongo_s.db.student_profile.find(username_query)
    result.extend(username_matching_documents)
    return result

def get_students():
    return list(mongo_s.db.student_profile.find())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(image):
    if image and allowed_file(image.filename):
        filename = f"{ObjectId()}.{image.filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "Image uploaded successfully.", "filename": filename}), 200
    else:
        return jsonify({"error": "Invalid image or file format."}), 400


def hash_password(password):
    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    return hashed_password  

def validate_password(password):
     """
     Validates password based on the following conditions:
     - At least 8 characters long
     - Contains at least one digit
     - Contains at least one uppercase letter
     - Contains at least one special character
     """
     if len(password) < 8:
         return False
     if not re.search("[0-9]", password):
         return False
     if not re.search("[A-Z]", password):
         return False
     # Assuming special characters are !@#$%^&*()-_+=
     if not re.search("[!@#$%^&*()\-_+=]", password):
         return False
     return True


# Create student profile 
@app.route('/create_student_profile', methods=['POST'])
def create_student_profile():
    password = request.form.get('password')
    print(password)
    if not validate_password(password):
        return jsonify('error : Not valid password')
    
    retype_password = request.form.get('retype_password')
    if password != retype_password:
        return jsonify('error : Password does not match')
    user_id = request.form.get('user_id', '')
    username = request.form.get('username', '')
    schoolkey = request.form.get('schoolkey')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    user_class = request.form.get('user_class', '')
    status_title = request.form.get('status_title', '')
    status_description = request.form.get('status_description', '')
    about = request.form.get('about', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    hashed_password = hash_password(password)
    parents = request.form.get('parents', '')

    if not is_student_user_id_unique(user_id):
        return jsonify({'error': 'User ID already exists'}), 400
    
    data = get_students()
    user_image = ''
    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                user_image = upload_image(image)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

    performance = {} 
    Attendance = {}
    Interest = {}
    parents = {}

    email_exists = any(item['personal_info']['contact']['email'] == email for item in data)
    phone_exists = any(item['personal_info']['contact']['phone'] == phone for item in data)
    useridname=any(item['user_id'] == user_id for item in data)

    if email_exists:
            return jsonify({"error": "This email is already exist"}), 400
    if phone_exists:
            return jsonify({"error": "This phone number is already exist"}), 400
    if useridname:
            return jsonify({"error": "This useridname is already exist"}), 400
    else:
        user_data = {
            "_id": str(ObjectId()),
            'user_id':user_id,
            'password': hashed_password,
            'username': username,
            'user_class': user_class,
            'schoolkey': schoolkey,
            'gender': gender,
            'dob': dob,
            'user_image': user_image,
            'status_title': status_title,
            'status_description': status_description,
            'personal_info': {
                'about': about,
                'contact': {
                    'phone': phone,
                    'email': email,
                    'address': address
                }
            },
            'performance': performance,
            'Attendance': Attendance,
            'Interest': Interest,
            'parents': parents
        }
        try:
            inserted_id = mongo_s.db.student_profile.insert_one(user_data).inserted_id
            inserted = mongo_s.db.student_profile.find_one({"_id": inserted_id})
            return jsonify({"_id": str(inserted["_id"])})
        except Exception as e:
            return jsonify({"error": "Error occurred while creating the class"}), 500

# Get student profile using user_id
@app.route('/get_user/<string:user_id>', methods=['GET'])
def get_user_profile(user_id):
    return get_student(user_id)

# update user profiledata requires user_id which is Unique
@app.route('/update_student_profile/<string:user_id>', methods=['PUT'])
def update_student_profile(user_id):
    try:
        user_data = mongo_s.db.student_profile.find_one({'user_id': user_id})
        _id = user_data['_id']
        # Get user data from the request
        username = request.form.get('username', user_data['username'])
        password = request.form.get('password', user_data['password'])
        hashed_password = hash_password(password)
        user_id = request.form.get('user_id', user_data['user_id'])

        user_class = request.form.get('user_class', user_data['user_class'])
        status_title = request.form.get('status_title', user_data['status_title'])
        status_description = request.form.get('status_description', user_data['status_description'])
        about = request.form.get('about', user_data['personal_info']['about'])
        phone = request.form.get('phone', user_data['personal_info']['contact']['phone'])
        email = request.form.get('email', user_data['personal_info']['contact']['email'])
        address = request.form.get('address', user_data['personal_info']['contact']['address'])
        performance = request.form.get('performance', user_data['performance'])
        Interest = request.form.get('Interest', user_data['Interest'])
        Attendance = request.form.get('Attendance', user_data['Attendance'])
        parents = request.form.get('parents', user_data['parents'])

        # Optional: Handle the user image update
        user_image = ''
        if 'image' in request.files:
                image = request.files['image', user_data['image']]
                if image and allowed_file(image.filename):
                    user_image = upload_image(image)
                else:
                    return jsonify({"error": "Invalid image or file format."}), 400

        user_data ={
                'user_id':user_id,
                'username': username,
                'password':hashed_password,
                'user_class': user_class,
                'user_image': user_image,
                'status_title': status_title,
                'status_description': status_description,
                'personal_info': {
                    'about': about,
                    'contact': {
                        'phone': phone,
                        'email': email,
                        'address': address
                    }
                },
                'performance': performance,
                'Attendance': Attendance,
                'Interest': Interest,
                'parents': parents
            }
        result = mongo_s.db.student_profile.update_one({"_id":_id},
                                                    {"$set": user_data})
        if result.modified_count == 0:
            return jsonify({"error": "student_profile not found"}), 404
        updated_entity = mongo_s.db.student_profile.find_one({"_id": _id})
        return jsonify(updated_entity), 200
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# search other user using phone, email, userid, username
@app.route('/search/<string:query>', methods=['GET'])
def search(query):
    # query = request.args.get('query', '').strip()
    try:
        if query:
            # Check if the query is a valid mobile number (all digits)
            if query.isdigit() and len(query) == 10:
                # Search for mobile number in all collections (student, parents, teacher)
                result = search_by_mobile_number(query)
            elif '@' in query:
                # Check if the query contains "@" (likely an email)
                # Search for email in all collections
                result = search_by_email(query)
            else:
                # Search for username or user ID in all collections
                result = search_by_username_or_user_id(query)
            return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "An error occurred.", "error": str(e)}), 500


# setting status of quiz after click by user on quiz 
@app.route('/setting_status/<string:quiz_id>/<string:student_id>', methods = ['PUT'])
def setting_status_of_quizz(quiz_id, student_id):

    new_quiz = {
        "quiz_id": quiz_id,
        "status": "seen"
    }
    # Define the update operation to add the new quiz to the quiz_data array
    update = {
        '$push': {
            'quiz_data': {
                '$each': [new_quiz],
            }
        }
    }

    result = mongo_s.db.student_profile.update_one({'_id': student_id}, update)
    return "Quizz seen",200


#adding quizz in student profile
@app.route('/update_student_quiz_data/<string:quiz_id>/<string:student_id>/<string:result>/<string:click>', methods=['PUT'])
def update_student_quiz_data(quiz_id, student_id, result, click):
    try:
        # Find the student by student_id
        student = mongo_s.db.student_profile.find_one({"_id": student_id})
        
        if student:
            # Check if the quiz_id already exists in quiz_data
            quiz_entry = next((entry for entry in student['quiz_data'] if entry.get('quiz_id') == quiz_id), None)

            if quiz_entry:
                quiz = mongo_q.db.quizes.find_one({"_id": quiz_id})
                # Update the existing quiz entry
                quiz_entry['subject'] = quiz.get('subject', '')
                quiz_entry['topic'] = quiz.get('topic', '')
                quiz_entry['class'] = quiz.get('class', '')
                quiz_entry['subtopic'] = quiz.get('subtopic', '')
                quiz_entry['language'] = quiz.get('language', '')            
                quiz_entry['result'] = result
                quiz_entry['clicked_on'] = click
                print(student)

                # Update the student's document with the modified quiz_data
                mongo_s.db.student_profile.update_one({"_id": student_id}, {"$set": student})

                return jsonify({"message": "Student quiz data updated successfully."}), 200
            else:
                return jsonify({"error": "Quiz not found in student data."}), 404
        else:
            return jsonify({"error": "Student not found."}), 404

    except Exception as e:
        return jsonify({"error": "An error occurred.", "error": str(e)}), 500


# getting accuracy of student
@app.route('/getting_accuracy/<string:student_id>', methods=['GET'])
def getting_accuracy(student_id):
    try:
        student = mongo_s.db.student_profile.find_one({"_id": student_id})
        result = []
        for res in student.get("quiz_data", []):
            try:
                result.append(res['result'])
            except KeyError:
                # Key 'result' not found in this quiz data, continue to the next iteration
                continue
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "An error occurred.", "error": str(e)}), 500






# Management Profile 

# functions to support API's
def is_management_user_id_unique(user_id):
    user = get_management(user_id)
    return user

def get_management(user_id):
    user = mongo_m.db.management_profile.find_one({'user_id': user_id})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to a string
    return jsonify(user)


def get_managements():
    return list(mongo_m.db.management_profile.find())

# Create management profile 
@app.route('/create_management_profile', methods=['POST'])
def create_management_profile():
    password = request.form.get('password')
    if not validate_password(password):
        return jsonify('error : Not valid password')
    retype_password = request.form.get('retype_password')
    if password != retype_password:
        return jsonify('error : Password does not match')
    user_id = request.form.get('user_id', '')
    username = request.form.get('username', '')
    schoolkey = request.form.get('schoolkey')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    user_class = request.form.get('user_class', '')
    status_title = request.form.get('status_title', '')
    about = request.form.get('about', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    hashed_password = hash_password(password)

    if not is_management_user_id_unique(user_id):
        return jsonify({'error': 'User ID already exists'}), 400
    
    user_image = ''
    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                user_image = upload_image(image)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

    school_performance = {} 
    data = get_managements()
    email_exists = any(item['personal_info']['contact']['email'] == email for item in data)
    phone_exists = any(item['personal_info']['contact']['phone'] == phone for item in data)
    useridname=any(item['user_id'] == user_id for item in data)

    if email_exists:
            return jsonify({"error": "This email is already exist"}), 400
    if phone_exists:
            return jsonify({"error": "This phone number is already exist"}), 400
    if useridname:
            return jsonify({"error": "This useridname is already exist"}), 400
    else:
        user_data = {
            "_id": str(ObjectId()),
            'user_id':user_id,
            'password': hashed_password,
            'username': username,
            'user_class': user_class,
            'schoolkey': schoolkey,
            'gender': gender,
            'dob': dob,
            'user_image': user_image,
            'status_title': status_title,
            'personal_info': {
                'about': about,
                'contact': {
                    'phone': phone,
                    'email': email,
                    'address': address
                }
            },
            'school_performance': school_performance,
        }
        try:
            inserted_id = mongo_m.db.management_profile.insert_one(user_data).inserted_id
            inserted = mongo_m.db.management_profile.find_one({"_id": inserted_id})
            return jsonify({"_id": str(inserted["_id"])})
        except Exception as e:
            return jsonify({"error": "Error occurred while creating the class"}), 500

# Get management profile using user_id
@app.route('/get_management_user/<string:user_id>', methods=['GET'])
def get__management_user_profile(user_id):
    return get_management(user_id)

# update user profiledata requires user_id which is Unique
@app.route('/update_management_profile/<string:user_id>', methods=['PUT'])
def update_management_profile(user_id):
    try:
        user_data = mongo_m.db.management_profile.find_one({'user_id': user_id})
        _id = user_data['_id']
        # Get user data from the request
        username = request.form.get('username', user_data['username'])
        password = request.form.get('password', user_data['password'])
        hashed_password = hash_password(password)
        user_id = request.form.get('user_id', user_data['user_id'])

        user_class = request.form.get('user_class', user_data['user_class'])
        status_title = request.form.get('status_title', user_data['status_title'])
        about = request.form.get('about', user_data['personal_info']['about'])
        phone = request.form.get('phone', user_data['personal_info']['contact']['phone'])
        email = request.form.get('email', user_data['personal_info']['contact']['email'])
        address = request.form.get('address', user_data['personal_info']['contact']['address'])
        school_performance = request.form.get('school_performance', user_data['school_performance'])

        # Optional: Handle the user image update
        user_image = ''
        if 'image' in request.files:
                image = request.files['image',user_data['user_image']]
                if image and allowed_file(image.filename):
                    user_image = upload_image(image)
                else:
                    return jsonify({"error": "Invalid image or file format."}), 400

        user_data ={
                'user_id':user_id,
                'username': username,
                'password':hashed_password,
                'user_class': user_class,
                'user_image': user_image,
                'status_title': status_title,
                'personal_info': {
                    'about': about,
                    'contact': {
                        'phone': phone,
                        'email': email,
                        'address': address
                    }
                },
                'school_performance': school_performance,
            }
        result = mongo_m.db.management_profile.update_one({"_id":_id},
                                                    {"$set": user_data})
        if result.modified_count == 0:
            return jsonify({"error": "management_profile not found"}), 404
        updated_entity = mongo_m.db.management_profile.find_one({"_id": _id})
        return jsonify(updated_entity), 200
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500
    






# Parents profile
parent_profile_collection=mongo_p.db.parent_profile

#get profile by userid
@app.route('/get_parent_data/<string:search_value>', methods=['GET'])
def fetch_parent_data(search_value):
    parent = get_parent(search_value)

    if parent:
        # Modify this part to select the specific fields you want to return
        parent_info = {
            "parent_name": parent.get("parent_name", ""),
            "parent_age": parent.get("parent_age", ""),
            "parent_gender": parent.get("parent_gender", ""),
            "parent_designation": parent.get("parent_designation", ""),
            "parent_description": parent.get("parent_description", ""),
            "parent_email": parent.get("personal_info", {}).get("contact", {}).get("parent_email", "")
        }
        return jsonify(parent_info)
    else:
        return jsonify({'error': 'User does not exist'}), 404


#get_parent_profile
@app.route('/get_parent_profile', methods=['GET'])
def get_parent_profile():
    parent_useridname = request.form.get("parent_useridname", '')
    parent_password = request.form.get("parent_password", '')
    session['parent_useridname'] = parent_useridname
    session_parent_useridname = session.get('parent_useridname', '')
    parent = get_parent_by_password_and_useridname(parent_password, parent_useridname)

    #fetch child data
    # child_data=get_student_data_by_parent_useridname(parent_useridname)

    if parent:
        parent_info = {
        "parent_useridname": parent["parent_useridname"],
        "parent_hashed_password": parent["parent_hashed_password"],
        "parent_name": parent["parent_name"],
        "parent_age": parent["parent_age"],
        "parent_gender": parent["parent_gender"],
        "parent_image": parent["parent_image"],
        "parent_about": parent["personal_info"]["parent_about"],
        "parent_phone": parent["personal_info"]["contact"]["parent_phone"],
        "parent_email": parent["personal_info"]["contact"]["parent_email"],
        "parent_address": parent["personal_info"]["contact"]["parent_address"],
        # "child_name":child_data['student_name'],
        # "child_image":child_data["student_image"]
        }
        return jsonify(parent_info)
    else:
        return jsonify({'error': 'User does not exist'}), 404


#create parent profile
@app.route('/create_parent_profile', methods=['GET', 'POST'])
def create_parent_profile():
    try:
        parent_password=request.form.get("parent_password", '')
        if not validate_password(parent_password):
            return jsonify('error : Not valid password')
        retype_password = request.form.get('retype_password')
        if parent_password != retype_password:
            return jsonify('error : Password does not match')
        parent_useridname=request.form.get("parent_useridname", '')
        parent_password=request.form.get("parent_password", '')
        parent_name = request.form.get('parent_name', '')
        parent_age = request.form.get('parent_age', '')
        parent_gender = request.form.get('parent_gender', '')
        
        parent_about = request.form.get('parent_about', '')
        parent_phone = request.form.get('parent_phone', '')
        parent_email = request.form.get('parent_email', '')
        parent_StreetAddress = request.form.get('parent_StreetAddress', '')
        parent_city=request.form.get('parent_city', '')
        parent_PostalCode=request.form.get('parent_PostalCode', '')
        parent_country=request.form.get('parent_country', '')
        parent_Apartment=request.form.get('parent_country', '')
        parent_state=request.form.get('parent_state', '')


        data=get_parents()
        parent_hashed_password = generate_password_hash(parent_password)
        
        user_image = ''
        if 'user_image' in request.files:
                image = request.files['user_image']
                if image and allowed_file(image.filename):
                    user_image = upload_image(image)
                else:
                    return jsonify({"error": "Invalid image or file format."}), 400

        email_exists = any(item['personal_info']['contact']['parent_email'] == parent_email for item in data)
        phone_exists = any(item['personal_info']['contact']['parent_phone'] == parent_phone for item in data)
        useridname=any(item['parent_useridname'] == parent_useridname for item in data)

        if email_exists:
              return jsonify({"error": "This email is already exist"}), 400
        if phone_exists:
              return jsonify({"error": "This phone number is already exist"}), 400
        if useridname:
              return jsonify({"error": "This useridname is already exist"}), 400
        else:
            create_parent(parent_useridname,parent_hashed_password,parent_name, user_image,parent_about, 
                          parent_phone, parent_email, parent_StreetAddress,parent_age,parent_gender,parent_city,
                          parent_PostalCode,parent_country,parent_Apartment,parent_state)

        return jsonify({"message": "Parent profile created successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500



#update parent info
@app.route('/update_parent/<string:useridname>', methods=['PUT'])
def update_parent_profile(useridname):
    parent_data = get_parent(useridname)
    if not parent_data:
        return jsonify({"error": "Parent not found"}), 404
    # Update parent information based on the received data

    # Example: Update the 'parent_name', 'parent_designation', and 'parent_description'
    parent_data['parent_useridname'] = request.form.get('parent_useridname', parent_data['parent_useridname'])
    parent_data['parent_name'] = request.form.get('parent_name', parent_data['parent_name'])
    parent_data['parent_age'] = request.form.get('parent_age', parent_data['parent_age'])
    parent_data['parent_gender'] = request.form.get('parent_gender', parent_data['parent_gender'])
    # Example: Update the 'parent_about', 'parent_phone', 'parent_email', and 'parent_address' within 'personal_info'
    parent_data['personal_info']['parent_about'] = request.form.get('parent_about', parent_data['personal_info']['parent_about'])
    parent_data['personal_info']['contact']['parent_phone'] = request.form.get('parent_phone', parent_data['personal_info']['contact']['parent_phone'])
    parent_data['personal_info']['contact']['parent_email'] = request.form.get('parent_email', parent_data['personal_info']['contact']['parent_email'])

    parent_separate_data =  parent_data['personal_info']['contact']['parent_address']
    
    parent_separate_data['parent_country'] = request.form.get('parent_country', parent_separate_data['parent_country'])
    parent_separate_data['parent_state'] = request.form.get('parent_state', parent_separate_data['parent_state'])
    parent_separate_data['parent_city'] = request.form.get('parent_city', parent_separate_data['parent_city'])
    parent_separate_data['parent_StreetAddress'] = request.form.get('parent_StreetAddress', parent_separate_data['parent_StreetAddress'])
    parent_separate_data['parent_Apartment'] = request.form.get('parent_Apartment', parent_separate_data['parent_Apartment'])
    parent_separate_data['parent_PostalCode'] = request.form.get('parent_PostalCode', parent_separate_data['parent_PostalCode'])

    user_image = ''
    if 'image' in request.files:
            image = request.files['image', parent_data['image']]
            if image and allowed_file(image.filename):
                user_image = upload_image(image)
                parent_data['image'] = user_image
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

     # Update password if provided
    new_password = request.form.get('new_password')
    if new_password:
        # You may want to add validation and hashing here
        parent_data['parent_hashed_password'] = generate_password_hash(new_password)

    # Save the updated parent data 
    update_parent(parent_data)

    return jsonify({"message": "Parent information updated successfully"}), 200

#database support function

# save parent info in database
def create_parent(parent_useridname,parent_hashed_password,parent_name, filename, parent_about, parent_phone, parent_email, parent_StreetAddress,parent_city,parent_PostalCode,parent_country,parent_Apartment,parent_state,parent_age,parent_gender):
    parent_profile_collection.create_index([('parent_useridname', 1)], unique=True)
    parent_profile_collection.create_index([('personal_info.contact.parent_email', 1)], unique=True)
    parent_profile_collection.create_index([('personal_info.contact.parent_phone', 1)], unique=True)
    parent = parent_profile_collection.insert_one({
        "parent_useridname":parent_useridname,
        "parent_hashed_password":parent_hashed_password,
        'parent_name': parent_name,
        "parent_age":parent_age,
        "parent_gender":parent_gender,
        'parent_image': filename,
        'personal_info': {
            'parent_about': parent_about,
            'contact': {
                'parent_phone': parent_phone,
                'parent_email': parent_email,
                'parent_address': {"parent_country":parent_country,
                                   "parent_state":parent_state,
                                   "parent_city":parent_city,
                                   "parent_StreetAddress":parent_StreetAddress,
                                   "parent_Apartment":parent_Apartment,
                                   "parent_PostalCode":parent_PostalCode


                                   }
            }
        }
    })
    return parent


#get all parent info
def get_parents():
    return list(parent_profile_collection.find({}))

#get parent by id
def get_parent_by_password_and_useridname(password, useridname):
    parent = parent_profile_collection.find_one({'parent_useridname': useridname})
    if parent:
        stored_password = parent.get('parent_hashed_password', '')
        realpass=check_password_hash(stored_password, password)
        if realpass:
            return parent
    print("db",parent)
    return None


#serch parent by their unique identity
def get_parent(search_value):
    parent = parent_profile_collection.find_one({'parent_useridname': search_value})
    if not parent:
        parent = parent_profile_collection.find_one({'personal_info.contact.parent_email': search_value})
    if not parent:
        parent = parent_profile_collection.find_one({'personal_info.contact.parent_phone': search_value})
    
    return parent


#update parent info
def update_parent(parent_data):
    # Update the parent document in the MongoDB collection based on its ObjectId
    parent_profile_collection.update_one(
        {'_id': ObjectId(parent_data['_id'])},
        {'$set': parent_data}
    )





# Teacher Profile
# --------------- DATABASE METHODS --------------

def create_teacher(user_data):

    hashed_password = generate_password_hash(user_data['profile']['useridname_password']['password'])

    mongo_t.db.teacher_profile.insert_one({
        'username': user_data['username'],
        'languages': user_data['languages'],
        'user_image': user_data['user_image'],

        'profile': {
            'status': {
                'user_designation': user_data['profile']['status']['user_designation'],
                'user_description': user_data['profile']['status']['user_description']
            },
            'about': user_data['profile']['about'],
            'useridname_password': {
                'userid_name': user_data['profile']['useridname_password']['userid_name'],
                'password': hashed_password
            },
            'contact': {
                'phone': user_data['profile']['contact']['phone'],
                'email': user_data['profile']['contact']['email'],
                'address': {
                    'house_no': user_data['profile']['contact']['address']['house_no'],
                    'street': user_data['profile']['contact']['address']['street'],
                    'postal_code': user_data['profile']['contact']['address']['postal_code'],
                    'city': user_data['profile']['contact']['address']['city'],
                    'state': user_data['profile']['contact']['address']['state']
                }
            }
        }
    })

def get_teachers():
    return list(mongo_t.db.teacher_profile.find({}))

def get_teacher(user_id):
    user = mongo_t.db.teacher_profile.find_one({'_id': ObjectId(user_id)})
    return user if user else None

def update_teacher(user_id, user_data):

    hashed_password = generate_password_hash(user_data['profile']['useridname_password']['password'])

    mongo_t.db.teacher_profile.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {
            'username': user_data['username'],
            'languages': user_data['languages'],
            'user_image': user_data['user_image'],

            'profile': {
                'status': {
                    'user_designation': user_data['profile']['status']['user_designation'],
                    'user_description': user_data['profile']['status']['user_description']
                },
                'about': user_data['profile']['about'],
                'useridname_password': {
                    'userid_name': user_data['profile']['useridname_password']['userid_name'],
                    'password': hashed_password
                },
                'contact': {
                    'phone': user_data['profile']['contact']['phone'],
                    'email': user_data['profile']['contact']['email'],
                    'address': {
                        'house_no': user_data['profile']['contact']['address']['house_no'],
                        'street': user_data['profile']['contact']['address']['street'],
                        'postal_code': user_data['profile']['contact']['address']['postal_code'],
                        'city': user_data['profile']['contact']['address']['city'],
                        'state': user_data['profile']['contact']['address']['state']
                    }
                }
            }
        }}
    )


# --------------- API METHODS --------------

@app.route('/get_teachers', methods=['GET'])
def get_teachers():
    teachers = get_teachers()

    for teacher in teachers:
        teacher['_id'] = str(teacher['_id'])
        
    return jsonify(teachers)

@app.route('/get_teacher/<string:user_id>', methods=['GET'])
def get_teacher_profile(user_id):
    user = get_teacher(user_id)
    if user:
        user['_id'] = str(user['_id'])
    else:
        return jsonify({'error': 'User does not exists!!'})
    return jsonify(user)


@app.route('/create_teacher', methods=['GET', 'POST'])
def create_teacher_profile():
    password = request.form.get('password')
    if not validate_password(password):
        return jsonify('error : Not valid password')
    
    retype_password = request.form.get('retype_password')
    if password != retype_password:
        return jsonify('error : Password does not match')
    username = request.form.get('username', '')
    languages = request.form.get('languages', '')

    user_image = ''
    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                user_image = upload_image(image)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

    user_designation = request.form.get('user_designation', '')
    user_description = request.form.get('user_description', '')

    about = request.form.get('user_about', '')

    userid_name = request.form.get('userid_name', '')
    password = request.form.get('password', '')
    if len(password) < 8:
        return jsonify({'error': 'Password must be from 8 characters!!'}), 404

    phone = request.form.get('phone', '')
    email = request.form.get('email', '')

    house_no = request.form.get('house_no', '')
    street = request.form.get('street', '')
    postal_code = request.form.get('postal_code', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')

    status = {
        'user_designation': user_designation,
        'user_description': user_description
    }

    useridname_password = {
        'userid_name': userid_name,
        'password': password
    }

    address = {
        'house_no': house_no,
        'street': street,
        'postal_code': postal_code,
        'city': city,
        'state': state
    }

    contact = {
        'phone': phone,
        'email': email,
        'address': address
    }

    profile = {
        'status': status,
        'about': about,
        'useridname_password': useridname_password,
        'contact': contact
    }

    user_data = {
        'username': username,
        'languages': languages,
        'user_image': user_image,
        'profile': profile
    }
    data = get_teachers()
    email_exists = any(item['personal_info']['contact']['email'] == email for item in data)
    phone_exists = any(item['personal_info']['contact']['phone'] == phone for item in data)
    useridname=any(item['user_id'] == userid_name for item in data)

    if email_exists:
            return jsonify({"error": "This email is already exist"}), 400
    if phone_exists:
            return jsonify({"error": "This phone number is already exist"}), 400
    if useridname:
            return jsonify({"error": "This useridname is already exist"}), 400
    else:   
        create_teacher(user_data)

    return jsonify(user_data)


@app.route('/update_teacher/<string:user_id>', methods=['PUT', 'POST'])
def update_user_profile(user_id):
    user_data = get_teacher(user_id)

    if not user_data:
        return jsonify({"error": "User not found"}), 404


    username = request.form.get('username', user_data['username'])
    languages = request.form.get('languages', user_data['languages'])

    user_designation = request.form.get('user_designation', user_data['profile']['status']['user_designation'])
    user_description = request.form.get('user_description', user_data['profile']['status']['user_description'])

    about = request.form.get('user_about', user_data['profile']['about'])

    userid_name = request.form.get('userid_name',  user_data['profile']['useridname_password']['userid_name'])
    password = request.form.get('password',  user_data['profile']['useridname_password']['password'])

    phone = request.form.get('phone', user_data['profile']['contact']['phone'])
    email = request.form.get('email', user_data['profile']['contact']['email'])

    house_no = request.form.get('house_no', user_data['profile']['contact']['address']['house_no'])
    street = request.form.get('street', user_data['profile']['contact']['address']['street'])
    postal_code = request.form.get('postal_code', user_data['profile']['contact']['address']['postal_code'])
    city = request.form.get('city', user_data['profile']['contact']['address']['city'])
    state = request.form.get('state', user_data['profile']['contact']['address']['state'])

    address = {
        'house_no': house_no,
        'street': street,
        'postal_code': postal_code,
        'city': city,
        'state': state
    }

    user_image = ''
    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                user_image = upload_image(image)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

    status = {
        'user_designation': user_designation,
        'user_description': user_description
    }

    useridname_password = {
        'userid_name': userid_name,
        'password': password
    }

    address = {
        'house_no': house_no,
        'street': street,
        'postal_code': postal_code,
        'city': city,
        'state': state
    }

    contact = {
        'phone': phone,
        'email': email,
        'address': address
    }

    profile = {
        'status': status,
        'about': about,
        'useridname_password': useridname_password,
        'contact': contact
    }

    new_user_data = {
        'username': username,
        'languages': languages,
        'user_image': user_image,

        'profile': profile
    }


    update_teacher(user_id, new_user_data)

    updated_user = get_teacher(user_id)
    updated_user['_id'] = str(updated_user['_id'])

    return jsonify(updated_user)




if __name__ == '__main__':
    app.run(debug=True)
