Here's a detailed `README.md` file explaining the API and its functionality:

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

4. Configure MongoDB URLs for different profile types (Students, Parents, Teachers, Managements, Quizes) in the `app.py` file by setting the `app.config['MONGO_URI']` values accordingly.

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

### Teacher Profile (Not implemented)

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

This README.md provides an overview of the API, its endpoints, installation instructions, and details on how to contribute. You can further customize it to include specific API usage examples and other relevant information as needed for your project.