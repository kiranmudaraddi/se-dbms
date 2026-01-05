# SE-DBMS - Student Efficient Database Management System

A comprehensive web-based Student Database Management System built with Flask and SQLite.

## 🌟 Features

- 👥 **User Authentication** - Admin, Faculty, and Student roles
- 📚 **Student Management** - Add, view, and manage student records
- 📖 **Subject Management** - Organize subjects by semester and credits
- 📊 **Marks Entry** - CIE (0-50) and SEE (0-100) marks management
- 📈 **Automatic Calculation** - SGPA and CGPA computation
- 📋 **Detailed Reports** - Comprehensive student performance reports
- 🎯 **Grade System** - Automatic grade point calculation

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap

## 📦 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/se-dbms.git
cd se-dbms
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

4. **Access the application:**
Open your browser and visit: `http://localhost:5000`

## 🔐 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Faculty | faculty | faculty123 |
| Student | student | student123 |

⚠️ **Important:** Change these credentials in production!

## 📁 Project Structure

```
sedbms/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── subjects.html
│   ├── marks.html
│   └── reports.html
└── static/
    └── style.css         # Custom styles
```

## 💾 Database Schema

### Tables

**1. users**
- User authentication and role management

**2. students**
- Student information (USN, Name, Branch, Semester, etc.)

**3. subjects**
- Subject details (Code, Name, Credits, Semester)

**4. marks**
- CIE and SEE marks storage

## 📊 Grading System

| Total Marks | Grade Point |
|-------------|-------------|
| 135-150     | 10          |
| 120-134     | 9           |
| 105-119     | 8           |
| 90-104      | 7           |
| 75-89       | 6           |
| 60-74       | 5           |
| Below 60    | 0 (Fail)    |

## 🎓 Features Overview

### Student Management
- Add new students with complete details
- View all students with their CGPA
- Delete students (Admin only)
- Search and filter capabilities

### Subject Management
- Add subjects with credits and semester
- Filter subjects by semester
- Manage Theory/Lab subjects

### Marks Management
- Enter CIE and SEE marks
- Update existing marks
- View complete marks history
- Automatic validation (CIE: 0-50, SEE: 0-100)

### Reports & Analytics
- Individual student performance reports
- Semester-wise SGPA calculation
- Overall CGPA computation
- Detailed grade breakdown

## 🚀 Usage

1. **Login** with provided credentials
2. **Add Students** - Navigate to Students section
3. **Add Subjects** - Set up subjects for each semester
4. **Enter Marks** - Input CIE and SEE marks
5. **View Reports** - Generate student performance reports

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.
## 👨‍💻 Author

**Kiran Mudaraddi**
- GitHub: [@kiranmudaraddi](https://github.com/kiranmudaraddi)
- Email: kiran.mudaraddi@gmail.com

## 🙏 Acknowledgments

- Built as a Database Management System project
- Flask framework for web development
- Bootstrap for responsive UI design

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

⭐ **Star this repository if you find it helpful!**
