from flask import Flask, jsonify, request, make_response, send_file, render_template
from pymongo import  errors
import re
from bson import ObjectId, Binary
from flask_pymongo import PyMongo
from werkzeug .security import generate_password_hash,check_password_hash
from pymongo.errors import OperationFailure

app = Flask(__name__)

# initializing Database
app.config["MONGO_URI"] = "mongodb://localhost:27017/Curriculum"
mongo = PyMongo(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/Students"
mongo_s = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Parents'
mongo_p = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Teachers'
mongo_t = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/Managements'
mongo_m = PyMongo(app)


# UPLOAD_FOLDER = 'static'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}  # Allowed file extensions for images
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def safe_create_index(collection, *args, **kwargs):
    try:
        return collection.create_index(*args, **kwargs)
    except OperationFailure as e:
        if "IndexKeySpecsConflict" in str(e):
            print(f"Index already exists on {collection.name}. Skipping creation.")
        else:
            raise

# For student profiles
safe_create_index(mongo_s.db.student_profile, [("user_id", 1)], unique=True)
safe_create_index(mongo_s.db.student_profile, [("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})


# For parent profiles
safe_create_index(mongo_p.db.parent_profile, [("parent_useridname", 1)], unique=True)
safe_create_index(mongo_p.db.parent_profile, [("personal_info.contact.parent_phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.parent_phone": {"$exists": True}})


# For teacher profiles
safe_create_index(mongo_t.db.teacher_profile, [("profile.useridname_password.userid_name", 1)], unique=True)
safe_create_index(mongo_t.db.teacher_profile, [("profile.contact.phone", 1)], unique=True, partialFilterExpression={"profile.contact.phone": {"$exists": True}})


# For management profiles
safe_create_index(mongo_m.db.management_profile, [("username", 1)], unique=True)
safe_create_index(mongo_m.db.management_profile, [("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})


# fetching all clases
@app.route('/get_all_clases', methods = ['GET'])
def get_all_classes():
    all_classes = []
    datas = list(mongo.db.school_classes.find())
    for cls in datas:
        all_classes.append(cls['name'])
    return all_classes


def check_for_user(phone, user_id):
    student_data = get_students()
    teacher_data = get_teachers()
    parent_data = get_parents()
    management_data = get_managements()

    phone_exists = False
    useridname_exists = False


    if phone:
        phone_exists = any(item['personal_info']['contact']['phone'] == phone for item in student_data)
        if not phone_exists:
            phone_exists = any(item['profile']['contact']['phone'] == phone for item in teacher_data)
        if not phone_exists:
            phone_exists = any(item['personal_info']['contact']['parent_phone'] == phone for item in parent_data)
        if not phone_exists:
            phone_exists = any(item['personal_info']['contact']['phone'] == phone for item in management_data)

    if user_id:
        useridname_exists = any(item['user_id'] == user_id for item in student_data)
        if not useridname_exists:
            useridname_exists = any(item['profile']['useridname_password']['userid_name'] == user_id for item in teacher_data)
        if not useridname_exists:
            useridname_exists = any(item['parent_useridname'] == user_id for item in parent_data)
        if not useridname_exists:
            useridname_exists = any(item['user_id'] == user_id for item in management_data)
    
    return [phone_exists, useridname_exists]

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

def search_student(search_value):
    student = mongo_s.db.student_profile.find_one({'user_id': search_value})
    if not student:
        student = mongo_s.db.student_profile.find_one({'personal_info.contact.email': search_value})
    if not student:
        student = mongo_s.db.student_profile.find_one({'personal_info.contact.phone': search_value})
    if student:
        student['_id'] = str(student['_id'])  # Convert ObjectId to string
        data = {
            "_id": student['_id'],
            "role": student['role'],
            "user_id": student['user_id'],
            "username": student['username'],
            "user_image": student['user_image'],
            'gender': student['gender'],
            'user_class': student['user_class'],
            'status_title': student['status_title'],
            'status_description': student['status_description'],
            'about': student['personal_info']['about'],
            'phone': student['personal_info']['contact']['phone'],
            'email': student['personal_info']['contact']['email'],
            'address': student['personal_info']['contact']['address'],
            'parents': student['parents']
        }
        return data
    return student

parent_profile_collection=mongo_p.db.parent_profile
#serch parent by their unique identity
def search_parent(search_value):
    parent = parent_profile_collection.find_one({'parent_useridname': search_value})
    if not parent:
        parent = parent_profile_collection.find_one({'personal_info.contact.parent_email': search_value})
    if not parent:
        parent = parent_profile_collection.find_one({'personal_info.contact.parent_phone': search_value})
    if parent:
        parent['_id'] = str(parent['_id'])
        data = {
            "_id": parent['_id'],
            "role": parent['role'],
            "user_id": parent['parent_useridname'],
            "username": parent['parent_name'],
            "user_image": parent['parent_image'],
            'gender': parent['parent_gender'],
            'about': parent['personal_info']['parent_about'],
            'status_title': parent['status_title'],
            'status_description': parent['status_description'],
            'phone': parent['personal_info']['contact']['parent_phone'],
            'email': parent['personal_info']['contact']['parent_email'],
            'address': parent['personal_info']['contact']['parent_address'],
            'child': parent['child']
        }
        return data
    return parent

def search_teacher(search_value):
    teacher = mongo_t.db.teacher_profile.find_one({'profile.useridname_password.userid_name': search_value})
    if not teacher:
        teacher = mongo_t.db.teacher_profile.find_one({'profile.contact.email': search_value})
    if not teacher:
        teacher = mongo_t.db.teacher_profile.find_one({'profile.contact.phone': search_value})
    if teacher:
        teacher['_id'] = str(teacher['_id']) 
        data = {
            "_id": teacher['_id'],
            "role": teacher['role'],
            "user_id": teacher['profile']['useridname_password']['userid_name'],
            "username": teacher['username'],
            'languages': teacher['languages'],
            "user_image": teacher['user_image'],
            'gender': teacher['gender'],
            'status_title': teacher['profile']['status']['user_designation'],
            'status_description': teacher['profile']['status']['user_description'],
            'about': teacher['profile']['about'],
            'phone': teacher['profile']['contact']['phone'],
            'email': teacher['profile']['contact']['email'],
            'address': teacher['profile']['contact']['address']
        }
        return data
    return teacher

def search_management(search_value):
    user_data = mongo_m.db.management_profile.find_one({'username': search_value})
    return user_data


def get_students():
    return list(mongo_s.db.student_profile.find())


@app.route('/get_image/<image_id>/<role>', methods = ['GET'])
def get_image(image_id, role):
    try:
        if role == "student":
            image_data = mongo_s.db.images.find_one({"_id": ObjectId(image_id)})
            if image_data:
                response = app.response_class(image_data["image_data"], mimetype='image/jpeg')
                return response
            else:
                return jsonify({"error": "Image not found"}), 404
        elif role == "teacher":
            image_data = mongo_t.db.images.find_one({"_id": ObjectId(image_id)})
            if image_data:
                response = app.response_class(image_data["image_data"], mimetype='image/jpeg')
                return response
            else:
                return jsonify({"error": "Image not found"}), 404
        elif role == "parent":
            image_data = mongo_p.db.images.find_one({"_id": ObjectId(image_id)})
            if image_data:
                response = app.response_class(image_data["image_data"], mimetype='image/jpeg')
                return response
            else:
                return jsonify({"error": "Image not found"}), 404
        elif role == "management":
            image_data = mongo_m.db.images.find_one({"_id": ObjectId(image_id)})
            if image_data:
                response = app.response_class(image_data["image_data"], mimetype='image/jpeg')
                return response
            else:
                return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return jsonify({"error": "Error fetching the image.", "details": str(e)}), 500


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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


# login
@app.route('/login_user', methods=['POST'])
def login_user():
    try:
        print('Hello')
        username = request.json.get('username')
        password = request.json.get('password')

        user_data = None

        if username.isdigit():  # Check if it's a mobile number
            user_data = mongo_s.db.student_profile.find_one({'personal_info.contact.phone': {'$exists': True, '$eq': username}})
            if user_data is None:
                user_data = mongo_p.db.parent_profile.find_one({'personal_info.contact.parent_phone': {'$exists': True, '$eq': username}})
            if user_data is None:
                user_data = mongo_t.db.teacher_profile.find_one({'profile.contact.phone': {'$exists': True, '$eq': username}})
        else:
            user_data = mongo_s.db.student_profile.find_one({'user_id': {'$exists': True, '$eq': username}})
            if user_data is None:
                user_data = mongo_p.db.parent_profile.find_one({'parent_useridname': {'$exists': True, '$eq': username}})
            if user_data is None:
                user_data = mongo_t.db.teacher_profile.find_one({'profile.useridname_password.userid_name': {'$exists': True, '$eq': username}})

        if user_data:
            user_data['_id'] = str(user_data['_id'])
            stored_password = None

            if 'password' in user_data:
                stored_password = user_data['password']
            elif 'profile' in user_data and 'useridname_password' in user_data['profile']:
                stored_password = user_data['profile']['useridname_password'].get('password')
            elif 'parent_hashed_password' in user_data:
                stored_password = user_data['parent_hashed_password']

            if stored_password:
                if check_password_hash(stored_password, password):
                    if "parent_useridname" in user_data:
                        return jsonify({"success": True, "message": 'Login successful', 'parent_useridname': user_data['parent_useridname'],
                                        'role': user_data['role'], '_id': user_data['_id']}), 200
                    elif "user_id" in user_data:
                        return jsonify({"success": True, "message": 'Login successful', '_id': user_data['_id'],
                                        'user_id': user_data['user_id'], 'role': user_data['role']}), 200
                    elif 'profile' in user_data and 'useridname_password' in user_data['profile']: 
                        return jsonify({"success": True, "message": 'Login successful', '_id': user_data['_id'],
                                        'userid_name': user_data['profile']['useridname_password']['userid_name'], 'role': user_data['role']}), 200
                else:
                    return jsonify(success=False, message='Wrong Password'), 401
            else:
                return jsonify(success=False, message='Password not found in user data'), 500
        else:
            return jsonify(success=False, message='Invalid credentials'), 401

    except Exception as e:
        # print(str(e))
        return jsonify({ "success":False, "error":'An error occurred',"error": str(e)}), 500


#  search other user using phone, email, userid, username

@app.route('/get_profile/<search_value>', methods=['GET'])
def get_profile(search_value):
   
    parent_profile = search_parent(search_value)
    teacher_profile = search_teacher(search_value)
    student_profile = search_student(search_value)
    management_profile = search_management(search_value)

    if parent_profile:
        return jsonify(parent_profile)
    elif teacher_profile:
        return jsonify(teacher_profile)
    elif student_profile:
        return jsonify(student_profile)
    elif management_profile:
        return jsonify(management_profile)
    else:
        return jsonify({"message": "Profile not found"})


# Create student profile 
@app.route('/create_student_profile', methods=['POST'])
def create_student_profile():
    password = request.form.get('password')
    if not validate_password(password):
        return jsonify({"error": "Not valid Password."}), 400
    
    retype_password = request.form.get('retype_password')
    if password != retype_password:
        return jsonify({"error": "Password not matched."}), 400
    user_id = request.form.get('user_id', '')
    username = request.form.get('username', '')
    region = request.form.get('region')
    schoolkey = request.form.get('schoolkey')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    user_class = request.form.get('user_class', '')
    status_title = request.form.get('status_title', '')
    status_description = request.form.get('status_description', '')
    about = request.form.get('about', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    street = request.form.get('street', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    pincode = request.form.get('pincode', '')
    hashed_password = generate_password_hash(password)
    parents = request.form.get('parents', '')

    address = {
        "street":street,
        "city":city,
        'state':state,
        "pincode":pincode
    }   
    if not is_student_user_id_unique(user_id):
        return jsonify({'error': 'User ID already exists'}), 400
    
    user_image = ''
    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_s.db.images.insert_one({"image_data": image_data}).inserted_id
                user_image = str(image_id)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

    performance = {} 
    Attendance = {}
    parents = {}

    result = check_for_user(phone,user_id)
    phone_exists = result[0]
    useridname = result[1]

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
            'region': region,
            'role':"student",
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
            'parents': parents
        }
        try:
            inserted_id = mongo_s.db.student_profile.insert_one(user_data).inserted_id
            inserted = mongo_s.db.student_profile.find_one({"_id": inserted_id})
            return jsonify({"_id": str(inserted["_id"]), 'user_id':inserted["user_id"], "role":inserted['role']})
        except Exception as e:
            return jsonify({"error": "Error occurred while creating the class", "error": str(e)}), 500

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
        username = request.form.get('username', user_data['username'])
        password = request.form.get('password')

        if password:
            if not validate_password(password):
                return jsonify({"error": "Not valid Password."}), 400
            hashed_password = generate_password_hash(password)
        else: 
            hashed_password = user_data['password']
        user_id = request.form.get('user_id')

        user_class = request.form.get('user_class', user_data['user_class'])
        status_title = request.form.get('status_title', user_data['status_title'])
        status_description = request.form.get('status_description', user_data['status_description'])
        about = request.form.get('about', user_data['personal_info']['about'])
        phone = request.form.get('phone')
        email = request.form.get('email', user_data['personal_info']['contact']['email'])
        street = request.form.get('street', user_data['personal_info']['contact']['address']['street'])
        city = request.form.get('city', user_data['personal_info']['contact']['address']['city'])
        state = request.form.get('state', user_data['personal_info']['contact']['address']['state'])
        pincode = request.form.get('pincode', user_data['personal_info']['contact']['address']['pincode'])


        address = {
            "street":street,
            "city":city,
            'state':state,
            "pincode":pincode
        }
        # Optional: Handle the user image update
        if 'user_image' in request.files:
                image = request.files['user_image']
                if image and allowed_file(image.filename):
                    image_data = Binary(image.read())
                    image_id = mongo_s.db.images.insert_one({"image_data": image_data}).inserted_id
                    user_image = str(image_id)
                else:
                    return jsonify({"error": "Invalid image or file format."}), 400
        else:
             user_image = user_data['user_image']
        result = check_for_user(phone,user_id)
        phone_exists = result[0]
        useridname = result[1]

        if phone != user_data['personal_info']['contact']['phone'] and phone_exists:
            return jsonify({"error": "This phone number is already exist"}), 400
        elif phone != user_data['personal_info']['contact']['phone'] and request.form.get('phone'):
            phone = request.form.get('phone')
        else:
            phone = user_data['personal_info']['contact']['phone']

        if useridname != user_data['user_id'] and useridname:
            return jsonify({"error": "This useridname is already exist"}), 400
        elif useridname != user_data['user_id'] and request.form.get('user_id'):
            useridname = request.form.get('user_id')
        else:
            useridname = user_data['user_id']

        user_data ={
                'user_id':useridname,
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
        
            }
        result = mongo_s.db.student_profile.update_one({"_id":_id},
                                                    {"$set": user_data})
        if result.modified_count == 0:
            return jsonify({"error": "No changes found"}), 400
        updated_entity = mongo_s.db.student_profile.find_one({"_id": _id})
        return jsonify(updated_entity), 200
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500



# Parents profile
parent_profile_collection=mongo_p.db.parent_profile

#get profile by userid
@app.route('/parent_data/<string:search_value>', methods=['GET'])
def fetch_parent_data(search_value):
    parent_data = mongo_p.db.parent_profile.find_one({'parent_useridname': search_value})
    if parent_data:
        # Modify this part to select the specific fields you want to return
        parent_info = {
            "parent_useridname":parent_data['parent_useridname'],
            'parent_name': parent_data['parent_name'],
            "parent_age":parent_data['parent_age'],
            "parent_DOB":parent_data["parent_DOB"],
            "parent_gender":parent_data['parent_gender'],
            "status_title":parent_data['status_title'],
            "status_description":parent_data['status_description'],

            'parent_about': parent_data['personal_info']['parent_about'],
            'parent_phone': parent_data['personal_info']['contact']['parent_phone'],
            'parent_email': parent_data['personal_info']['contact']['parent_email'],
            "parent_state":parent_data['personal_info']['contact']['parent_address']['parent_state'],
            "parent_StreetAddress":parent_data['personal_info']['contact']['parent_address']['parent_StreetAddress'],
            "parent_city":parent_data['personal_info']['contact']['parent_address']['parent_city'],
            "parent_PostalCode":parent_data['personal_info']['contact']['parent_address']['parent_PostalCode'],
            "parent_image":parent_data['parent_image']
        }
        return jsonify(parent_info)
    else:
        return jsonify({'error': 'User does not exist'}), 400



#create parent profile
@app.route('/create_parent_profile', methods=['GET', 'POST'])
def create_parent_profile():
        parent_password=request.form.get("parent_password", '')
        if not validate_password(parent_password):
            return jsonify({"error": "Not valid Password."}), 400
        retype_password = request.form.get('retype_password')
        if parent_password != retype_password:
            return jsonify({"error": "Password not matched."}), 400
        parent_useridname=request.form.get("parent_useridname", '')
        parent_name = request.form.get('parent_name', '')
        region = request.form.get('region', '')
        parent_age = request.form.get('parent_age', '')
        parent_gender = request.form.get('parent_gender', '')
        status_title = request.form.get('status_title', '')
        status_description = request.form.get('status_description', '')
        
        parent_about = request.form.get('parent_about', '')
        parent_phone = request.form.get('parent_phone', '')
        parent_email = request.form.get('parent_email', '')
        parent_DOB=request.form.get('parent_DOB','')
        parent_StreetAddress = request.form.get('parent_StreetAddress', '')
        parent_city=request.form.get('parent_city', '')
        parent_PostalCode=request.form.get('parent_PostalCode', '')
        parent_country=request.form.get('parent_country', '')
        parent_state=request.form.get('parent_state', '')

        parent_hashed_password = generate_password_hash(parent_password)
        
        user_image = ''
        if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_p.db.images.insert_one({"image_data": image_data}).inserted_id
                user_image = str(image_id)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

        result = check_for_user(parent_phone,parent_useridname)

        phone_exists = result[0]
        useridname = result[1]

        if phone_exists:
              return jsonify({"error": "This phone number is already exist"}), 400
        if useridname:
              return jsonify({"error": "This useridname is already exist"}), 400
        else:
            user_data = ({
                "_id": str(ObjectId()),
                "region":region,
                "parent_useridname":parent_useridname,
                "parent_hashed_password":parent_hashed_password,
                'parent_name': parent_name,
                "parent_age":parent_age,
                "parent_DOB":parent_DOB,
                "role":"parent",
                'parent_image': user_image,
                "parent_gender":parent_gender,
                "status_title":status_title,
                "status_description":status_description,
                "child": [],
                'personal_info': {
                    'parent_about': parent_about,
                    'contact': {
                        'parent_phone': parent_phone,
                        'parent_email': parent_email,
                        'parent_address': {"parent_country":parent_country,
                                        "parent_state":parent_state,
                                        "parent_StreetAddress":parent_StreetAddress,
                                        "parent_city":parent_city,
                                        "parent_PostalCode":parent_PostalCode
                                        }
                    }
                }
            })
            try:
                inserted_id = mongo_p.db.parent_profile.insert_one(user_data).inserted_id
                inserted = mongo_p.db.parent_profile.find_one({"_id": inserted_id})
                return jsonify({"_id": str(inserted["_id"]), 'parent_useridname':inserted["parent_useridname"], "role":inserted['role']})
            except Exception as e:
                return jsonify({"error": "Error occurred while creating the class", "error": str(e)}), 500




#update parent info
@app.route('/update_parent/<string:useridname>', methods=['PUT'])
def update_parent_profile(useridname):
    parent_data = mongo_p.db.parent_profile.find_one({'parent_useridname': useridname})
    if not parent_data:
        return jsonify({"error": "Parent not found"}), 400
    # Update parent information based on the received data

    # Example: Update the 'parent_name', 'parent_designation', and 'parent_description'
    user_id = request.form.get('parent_useridname')
    parent_data['parent_name'] = request.form.get('parent_name', parent_data['parent_name'])
    parent_data['personal_info']['parent_about'] = request.form.get('parent_about', parent_data['personal_info']['parent_about'])
    phone = request.form.get('parent_phone')
    parent_data['personal_info']['contact']['parent_email'] = request.form.get('parent_email', parent_data['personal_info']['contact']['parent_email'])
    parent_data['status_title'] = request.form.get('status_title', parent_data['status_title'])
    parent_data['status_description'] = request.form.get('status_description', parent_data['status_description'])
    parent_separate_data =  parent_data['personal_info']['contact']['parent_address']
    
    parent_separate_data['parent_country'] = request.form.get('parent_country', parent_separate_data['parent_country'])
    parent_separate_data['parent_state'] = request.form.get('parent_state', parent_separate_data['parent_state'])
    parent_separate_data['parent_city'] = request.form.get('parent_city', parent_separate_data['parent_city'])
    parent_separate_data['parent_StreetAddress'] = request.form.get('parent_StreetAddress', parent_separate_data['parent_StreetAddress'])
    parent_separate_data['parent_PostalCode'] = request.form.get('parent_PostalCode', parent_separate_data['parent_PostalCode'])

    result = check_for_user(phone,user_id)
    phone_exists = result[0]
    useridname = result[1]

    if phone != parent_data['personal_info']['contact']['parent_phone'] and phone_exists:
        return jsonify({"error": "This phone number is already exist"}), 400
    elif phone != parent_data['personal_info']['contact']['parent_phone'] and request.form.get('parent_phone'):
        parent_data['personal_info']['contact']['parent_phone'] = request.form.get('parent_phone')

    if useridname != parent_data['parent_useridname'] and useridname:
        return jsonify({"error": "This useridname is already exist"}), 400
    elif useridname != parent_data['parent_useridname'] and request.form.get('parent_useridname'):
        parent_data['parent_useridname'] = request.form.get('parent_useridname')

    
    if 'user_image' in request.files:
        image = request.files['user_image']
        if image and allowed_file(image.filename):
            image_data = Binary(image.read())
            image_id = mongo_p.db.images.insert_one({"image_data": image_data}).inserted_id
            parent_data['parent_image'] = str(image_id)
        else:
            return jsonify({"error": "Invalid image or file format."}), 400

    new_password = request.form.get('new_password')
    if new_password:
        parent_data['parent_hashed_password'] = generate_password_hash(new_password)

    update_parent(parent_data)

    return jsonify({"message": "Parent information updated successfully"}), 200



#database support function
#get all parent info
def get_parents():
    return list(parent_profile_collection.find({}))

#serch parent by their unique identity
def get_parent(parent_useridname):
    user = mongo_p.db.parent_profile.find_one({'parent_useridname': parent_useridname})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to a string
    return jsonify(user)


#update parent info
def update_parent(parent_data):
    # Update the parent document in the MongoDB collection based on its ObjectId
    parent_profile_collection.update_one(
        {'_id': parent_data['_id']},
        {'$set': parent_data}
    )


# Teacher Profile
# --------------- DATABASE METHODS --------------

def create_teacher(user_data):

    hashed_password = generate_password_hash(user_data['profile']['useridname_password']['password'])

    inserted_i = mongo_t.db.teacher_profile.insert_one({
        'username': user_data['username'],
        'languages': user_data['languages'],
        'user_image': user_data['user_image'],
        'gender': user_data['gender'],
        'dob': user_data['dob'],
        'role': "teacher",
        'region': user_data['region'],
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
    }).inserted_id
    inserted = get_teacher(ObjectId(inserted_i))
    return inserted

def get_teachers():
    return list(mongo_t.db.teacher_profile.find({}))

def get_teacher(user_id):
    user = mongo_t.db.teacher_profile.find_one({'_id': ObjectId(user_id)})
    return user if user else None

def update_teacher(user_id, user_data):

    # hashed_password = generate_password_hash(user_data['profile']['useridname_password']['password'])

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
                    'password': user_data['profile']['useridname_password']['password']
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

@app.route('/get_teacher_profile/<string:user_id>', methods = ['GET'])
def get_teacher_profile(user_id):
    user_data = mongo_t.db.teacher_profile.find_one({'profile.useridname_password.userid_name': user_id})
    if user_data:
        info = {
        'username': user_data['username'],
        'languages': user_data['languages'],
        'user_image': user_data['user_image'],
        'gender': user_data['gender'],
        'dob': user_data['dob'],
        'profile': {
            'status': {
                'user_designation': user_data['profile']['status']['user_designation'],
                'user_description': user_data['profile']['status']['user_description']
            },
            'about': user_data['profile']['about'],
            'useridname_password': {
                'userid_name': user_data['profile']['useridname_password']['userid_name'],
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
    }

    return jsonify(info) 
# --------------- API METHODS --------------

@app.route('/get_teachers_profile', methods=['GET'])
def get_teachers_profile():
    teachers = get_teachers()

    for teacher in teachers:
        teacher['_id'] = str(teacher['_id'])
        
    return jsonify(teachers)

@app.route('/get_teacher/<string:user_id>', methods=['GET'])
def get_teacher_prof(user_id):
    user = mongo_t.db.teacher_profile.find_one({'profile.useridname_password.userid_name': user_id})
    if user:
        teacher_info = {
            "username": user['username'],
            'user_image': user['user_image'],
            'languages': user['languages'],
            "userid_name":user['profile']['useridname_password']['userid_name'],
            "gender": user['gender'],
            "about": user['profile']['about'],
            'status': {
                'user_designation': user['profile']['status']['user_designation'],
                'user_description': user['profile']['status']['user_description']
            },
            'email': user['profile']['contact']['email'],
        }
        return jsonify(teacher_info)
    else:
        return jsonify({'error': 'User does not exists!!'}), 401
    


@app.route('/create_teacher', methods=['GET', 'POST'])
def create_teacher_profile():
    password = request.form.get('password')
    if not validate_password(password):
        return jsonify({"error": "Not valid Password."}), 400
    
    retype_password = request.form.get('retype_password')
    if password != retype_password:
        return jsonify({"error": "Password not matched."}), 400
    username = request.form.get('username', '')
    languages = request.form.get('languages', '')

    user_image = ''
    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_t.db.images.insert_one({"image_data": image_data}).inserted_id
                user_image = str(image_id)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400


    user_designation = request.form.get('user_designation', '')
    user_description = request.form.get('user_description', '')

    about = request.form.get('user_about', '')
    region = request.form.get('region','')
    userid_name = request.form.get('userid_name', '')
    password = request.form.get('password', '')

    gender = request.form.get('gender', '')
    dob = request.form.get('dob', '')

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
        'gender': gender,
        'region': region,
        'dob': dob,
        'profile': profile
    }
    data = get_teachers()
    phone_exists = any(item['profile']['contact']['phone'] == phone for item in data)
    useridname=any(item['profile']['useridname_password']['userid_name'] == userid_name for item in data)

    if phone_exists:
            return jsonify({"error": "This phone number is already exist"}), 400
    if useridname:
            return jsonify({"error": "This useridname is already exist"}), 400
    else:
        newdata = create_teacher(user_data)
        newdata['_id'] = str(newdata['_id'])
        return jsonify(newdata)


@app.route('/update_teacher/<string:user_id>', methods=['PUT', 'POST'])
def update_user_profile(user_id):
    user_data = mongo_t.db.teacher_profile.find_one({'profile.useridname_password.userid_name': user_id})

    if not user_data:
        return jsonify({"error": "User not found"}), 400

    username = request.form.get('username', user_data['username'])
    languages = request.form.get('languages', user_data['languages'])

    phone = request.form.get('phone')
    user_id = request.form.get('userid_name')
    user_designation = request.form.get('user_designation', user_data['profile']['status']['user_designation'])
    user_description = request.form.get('user_description', user_data['profile']['status']['user_description'])

    about = request.form.get('user_about', user_data['profile']['about'])
        
    if request.form.get('password'):
        password = generate_password_hash(request.form.get('password'))
    else:
        password = user_data['profile']['useridname_password']['password']

    result = check_for_user(phone,user_id)
    phone_exists = result[0]
    useridname = result[1]

    if phone != user_data['profile']['contact']['phone'] and phone_exists:
        return jsonify({"error": "This phone number is already exist"}), 400
    elif phone != user_data['profile']['contact']['phone'] and request.form.get('phone'):
        phone = request.form.get('phone')
    else:
        phone = user_data['profile']['contact']['phone']

    if useridname != user_data['profile']['useridname_password']['userid_name'] and useridname:
        return jsonify({"error": "This useridname is already exist"}), 400
    elif useridname != user_data['profile']['useridname_password']['userid_name'] and request.form.get('userid_name'):
        useridname = request.form.get('userid_name')
    else:
        useridname = user_data['profile']['useridname_password']['userid_name']   

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

    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_t.db.images.insert_one({"image_data": image_data}).inserted_id
                user_image = str(image_id)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

    else:
        user_image = user_data['user_image']

    status = {
        'user_designation': user_designation,
        'user_description': user_description
    }

    useridname_password = {
        'userid_name': useridname,
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
    user_object_id = user_data['_id']
    update_teacher(user_object_id, new_user_data)

    updated_user = mongo_t.db.teacher_profile.find_one({'profile.useridname_password.userid_name': user_id})

    return jsonify({"message":"user profile updated"}), 200




# Management Profile 

# functions to support API's
def get_management(username):
    user = mongo_m.db.management_profile.find_one({'username': username})
    if user:
        return jsonify(user)
    else:
        return None

def get_managements():
    return list(mongo_m.db.management_profile.find())

# Create management profile 
@app.route('/create_management_profile', methods=['POST'])
def create_management_profile():

    username = request.form.get('username')
    doi = request.form.get('doi')
    phone = request.form.get('phone')
    alt_phone = request.form.get('alt_phone','')
    email = request.form.get('email')
    alt_email = request.form.get('alt_email', '')
    fax = request.form.get('fax')
    schoolcode = request.form.get('schoolcode')
    from_class = request.form.get('from_class')
    to_class = request.form.get('to_class')
    motto = request.form.get('motto','')
    school_about = request.form.get('school_about')
    vision = request.form.get('vision', '')
    mission = request.form.get('mission')
    chairman_name = request.form.get('chairman_name','')
    chairman_image = ''
    if 'chairman_image' in request.files:
            image = request.files['chairman_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_m.db.images.insert_one({"image_data": image_data}).inserted_id
                chairman_image = str(image_id)

    principle_name = request.form.get('principle_name', '')
    if 'principle_image' in request.files:
            image = request.files['principle_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_m.db.images.insert_one({"image_data": image_data}).inserted_id
                principle_image = str(image_id)

    facilities = request.form.get('facilities')
    extracurricular_activities = request.form.get('extracurricular_activities')
    special_programs = request.form.get('special_programs')
    achievements = request.form.get('achievements')
    school_performance = []

    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    country = request.form.get('country')
    pincode = request.form.get('pincode')

    address = {
        "street":street,
        "city":city,
        'state':state,
        "pincode":pincode,
        "country":country
    }
    
    user_image = ''
    if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_m.db.images.insert_one({"image_data": image_data}).inserted_id
                user_image = str(image_id)
            else:
                return jsonify({"error": "Invalid image or file format."}), 400

    user_data = {
        "_id": str(ObjectId()),
        'username': username,
        'user_image': user_image,
        'role':"management",
        'schoolcode': schoolcode,
        'doi': doi,   
        'contact': {
            'phone': phone,
            'alt_phone': alt_phone,
            'email': email,
            'alt_email': alt_email,
            'fax': fax,
            'address': address
        },
        'from_class': from_class,
        'to_class': to_class,
        'motto': motto,
        'school_about': school_about,
        'vision': vision,
        'mission': mission,
        'chairman':{
            'chairman_name': chairman_name,
            'chairman_image': chairman_image 
            },
        'principle': {
            'principle_name': principle_name,
            'principle_name': principle_image 
            },
        'facilities': facilities,
        'extracurricular_activities': extracurricular_activities,
        'special_programs': special_programs,
        'achievements': achievements,
        'school_performance': school_performance,
    }
    try:
        inserted_id = mongo_m.db.management_profile.insert_one(user_data).inserted_id
        inserted = mongo_m.db.management_profile.find_one({"_id": inserted_id})
        return jsonify(inserted), 200
    except Exception as e:
        return jsonify({"error": "Error occurred while creating the class", "details": str(e)}), 500

# Get management profile using user_id
@app.route('/get_management_user/<string:username>', methods=['GET'])
def get__management_user_profile(username):
    return get_management(username)

# update user profiledata requires user_id which is Unique
@app.route('/update_management_profile/<string:username>', methods=['PUT'])
def update_management_profile(username):
    try:
        user_data = mongo_m.db.management_profile.find_one({'username': username})
        if user_data is None:
            return jsonify({"error": "Management profile not found"}), 404

        _id = user_data['_id']

        user_image = user_data.get('user_image', '')
        if 'user_image' in request.files:
            image = request.files['user_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_m.db.images.insert_one({"image_data": image_data}).inserted_id
                user_image = str(image_id)
                user_data['user_image'] = user_image
            else:
                return jsonify({"error": "Invalid image or file format."}), 400
        

        chairman_name = request.form.get('chairman_name', user_data.get('chairman', {}).get('chairman_name', ''))
        chairman_image = user_data.get('chairman', {}).get('chairman_image', '')
        if 'chairman_image' in request.files:
            image = request.files['chairman_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_m.db.images.insert_one({"image_data": image_data}).inserted_id
                chairman_image = str(image_id)

        user_data['chairman'] = {
            'chairman_name': chairman_name,
            'chairman_image': chairman_image
        }

        principle_name = request.form.get('principle_name', user_data.get('principle', {}).get('principle_name', ''))
        principle_image = user_data.get('principle', {}).get('principle_image', '')
        if 'principle_image' in request.files:
            image = request.files['principle_image']
            if image and allowed_file(image.filename):
                image_data = Binary(image.read())
                image_id = mongo_m.db.images.insert_one({"image_data": image_data}).inserted_id
                principle_image = str(image_id)

        user_data['principle'] = {
            'principle_name': principle_name,
            'principle_image': principle_image
        }

        user_data['doi'] = request.form.get('doi', user_data.get('doi', ''))
        user_data['schoolcode'] = request.form.get('schoolcode', user_data.get('schoolcode', ''))
        user_data['from_class'] = request.form.get('from_class', user_data.get('from_class', ''))
        user_data['to_class'] = request.form.get('to_class', user_data.get('to_class', ''))
        user_data['motto'] = request.form.get('motto', user_data.get('motto', ''))
        user_data['school_about'] = request.form.get('school_about', user_data.get('school_about', ''))
        user_data['vision'] = request.form.get('vision', user_data.get('vision', ''))
        user_data['mission'] = request.form.get('mission', user_data.get('mission', ''))
        user_data['facilities'] = request.form.get('facilities', user_data.get('facilities', ''))
        user_data['extracurricular_activities'] = request.form.get('extracurricular_activities', user_data.get('extracurricular_activities', ''))
        user_data['special_programs'] = request.form.get('special_programs', user_data.get('special_programs', ''))
        user_data['achievements'] = request.form.get('achievements', user_data.get('achievements', ''))
        user_data['school_performance'] = request.form.get('school_performance', user_data.get('school_performance', ''))
        

        phone = request.form.get('phone', user_data.get('contact', {}).get('phone', ''))
        alt_phone = request.form.get('alt_phone', user_data.get('contact', {}).get('alt_phone', ''))
        email = request.form.get('email', user_data.get('contact', {}).get('email', ''))
        alt_email = request.form.get('alt_email', user_data.get('contact', {}).get('alt_email', ''))
        fax = request.form.get('fax', user_data.get('contact', {}).get('fax', ''))


        street = request.form.get('street', user_data.get('contact', {}).get('address', {}).get('street', ''))
        city = request.form.get('city', user_data.get('contact', {}).get('address', {}).get('city', ''))
        state = request.form.get('state', user_data.get('contact', {}).get('address', {}).get('state', ''))
        country = request.form.get('country', user_data.get('contact', {}).get('address', {}).get('country', ''))
        pincode = request.form.get('pincode', user_data.get('contact', {}).get('address', {}).get('pincode', ''))

        address = {
            "street": street,
            "city": city,
            'state': state,
            "pincode": pincode,
            "country": country
        }

        user_data['contact'] = {
            'phone': phone,
            'alt_phone': alt_phone,
            'email': email,
            'alt_email': alt_email,
            'fax': fax,
            'address': address
        }

        result = mongo_m.db.management_profile.update_one({"_id": _id}, {"$set": user_data})
        if result.modified_count == 0:
            return jsonify({"error": "Management profile not found"}), 404

        updated_entity = mongo_m.db.management_profile.find_one({"_id": _id})
        return jsonify(updated_entity), 200

    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")