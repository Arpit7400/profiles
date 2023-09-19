Certainly! Here's the full README.md file with the "Teacher Profile" section added:

```markdown
# Student Management API

This API provides functionality for managing student, parent, teacher, and management profiles. It includes features for user registration, profile management, and searching for users by various criteria. Additionally, it supports handling student quiz data and generating statistics.

## Technologies Used

- Python
- Flask (a Python web framework)
- MongoDB (a NoSQL database)
- PyMongo (a Python driver for MongoDB)
- Werkzeug (for security)

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/Arpit7400/profiles.git
   ```

2. Install the required Python packages using pip:

   ```bash
   pip install Flask Flask-PyMongo
   ```

3. Make sure you have MongoDB installed and running on your local machine. You can download it from [here](https://www.mongodb.com/try/download/community).

4. Configure MongoDB URLs for different profile types (Students, Parents, Teachers, Managements, Quizzes) in the `app.py` file by setting the `app.config['MONGO_URI']` values accordingly.

5. Run the Flask application:

   ```bash
   python app.py
   ```

6. The API should now be running locally at `http://localhost:5000`.

## API Endpoints

### Student Profile

#### Create Student Profile
- **Endpoint:** `/create_student_profile`
- **Method:** POST
- **Description:** Create a new student profile with the provided information, including user ID, password, personal details, and more.
- **Request Body:** JSON with student profile data.
- **Response:** JSON with the created student profile data.

#### Get Student Profile by User ID
- **Endpoint:** `/get_user/<string:user_id>`
- **Method:** GET
- **Description:** Retrieve a student's profile using their user ID.
- **Response:** JSON with the student's profile data.

#### Update Student Profile
- **Endpoint:** `/update_student_profile/<string:user_id>`
- **Method:** PUT
- **Description:** Update a student's profile data using their user ID.
- **Request Body:** JSON with the updated student profile data.
- **Response:** JSON with the updated student profile data.

#### Search for Users
- **Endpoint:** `/search/<string:query>`
- **Method:** GET
- **Description:** Search for users by username, user ID, email, or phone number.
- **Response:** JSON with matching user profiles.

#### Set Status of Quiz
- **Endpoint:** `/setting_status/<string:quiz_id>/<string:student_id>`
- **Method:** PUT
- **Description:** Set the status of a quiz as "seen" for a specific student.
- **Response:** Success message.

#### Update Student Quiz Data
- **Endpoint:** `/update_student_quiz_data/<string:quiz_id>/<string:student_id>/<string:result>/<string:click>`
- **Method:** PUT
- **Description:** Update a student's quiz data, including the result and click status for a specific quiz.
- **Response:** Success message.

#### Get Student Accuracy
- **Endpoint:** `/getting_accuracy/<string:student_id>`
- **Method:** GET
- **Description:** Retrieve the accuracy data for a student based on their quiz results.
- **Response:** JSON with quiz accuracy data.

### Management Profile

#### Check Management User ID Uniqueness
- **Endpoint:** `/check_management_user_id/<string:user_id>`
- **Method:** GET
- **Description:** Check if a management user ID is unique.
- **Response:** JSON with the result indicating whether the user ID is unique.

#### Get Management Profile by User ID
- **Endpoint:** `/get_management_user/<string:user_id>`
- **Method:** GET
- **Description:** Retrieve a management user's profile using their user ID.
- **Response:** JSON with the management user's profile data.

#### Get All Management Profiles
- **Endpoint:** `/get_all_management_profiles`
- **Method:** GET
- **Description:** Retrieve all management profiles.
- **Response:** JSON with a list of all management profiles.

#### Create Management Profile
- **Endpoint:** `/create_management_profile`
- **Method:** POST
- **Description:** Create a new management profile with the provided information, including user ID, password, personal details, and more.
- **Request Body:** JSON with management profile data.
- **Response:** JSON with the created management profile data.

#### Update Management Profile
- **Endpoint:** `/update_management_profile/<string:user_id>`
- **Method:** PUT
- **Description:** Update a management user's profile data using their user ID.
- **Request Body:** JSON with the updated management profile data.
- **Response:** JSON with the updated management profile data.

### Parent Profile

#### Get Parent Data by User ID or Email or Phone Number
- **Endpoint:** `/get_parent_data/<string:search_value>`
- **Method:** GET
- **Description:** Retrieve parent profile data using their user ID, email, or phone number.
- **Response:** JSON with parent profile data.

#### Get Parent Profile by User ID and Password
- **Endpoint:** `/get_parent_profile`
- **Method:** GET
- **Description:** Retrieve a parent's profile by providing their user ID and password.
- **Response:** JSON with parent profile data.

#### Create Parent Profile
- **Endpoint:** `/create_parent_profile`
- **Method:** POST
- **Description:** Create a new parent profile with the provided information, including user ID, password, personal details, and more.
- **Request Body:** JSON with parent profile data.
- **Response:** JSON with the created parent profile data.

#### Update Parent Profile
- **Endpoint:** `/update_parent/<string:useridname>`
- **Method:** PUT
- **Description:** Update a parent's profile data using their user ID.
- **Request Body:** JSON with the updated parent profile data.
- **Response:** Success message.

### Teacher Profile

#### Create Teacher Profile

This method allows you to create a new teacher profile with the provided information.

```python
def create_teacher(user_data):
    # ...
```

#### Get Teachers

This method retrieves a list of all teacher profiles.

```python
def get_teachers():
    # ...
```

#### Get Teacher by User ID

This method retrieves a teacher's profile by providing their user ID.

```python
def get_teacher(user_id):
    # ...
```

#### Update Teacher Profile

This method allows you to update a teacher's profile data using their user ID.

```python
def update_teacher(user_id, user_data):
    # ...
```

## Contributing

If you want to contribute to this project, please follow these steps:

1. Fork this repository.
2. Create a new branch for your feature or bug fix: `git checkout -b feature/your-feature`.
3. Make your changes and commit them: `git commit -m "Add your feature or fix"`.
4. Push your changes to your fork: `git push origin feature/your-feature`.
5. Create a pull request to the original repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

This README.md file now includes the "Teacher Profile" section along with the previously provided sections. You can use this updated file for

 your project documentation.