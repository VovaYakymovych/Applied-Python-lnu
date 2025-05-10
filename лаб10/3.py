import xml.etree.ElementTree as ET
import json
from statistics import mean


class StudentManager:
    def __init__(self, file_path):
        self.file_path = file_path
        try:
            self.tree = ET.parse(file_path)
            self.root = self.tree.getroot()
        except (FileNotFoundError, ET.ParseError):
            # Create a new XML file if it doesn't exist or has issues
            self.root = ET.Element("students")
            self.tree = ET.ElementTree(self.root)
            self.save()

    def save(self):
        self.tree.write(self.file_path, encoding='utf-8', xml_declaration=True)

    def add_student(self, student_id, last_name, first_name, birth_year, course, grades):
        # Check if student already exists
        if self.find_student(student_id) is not None:
            raise ValueError(f"Student with ID {student_id} already exists")

        # Create new student element
        student = ET.SubElement(self.root, "student")
        ET.SubElement(student, "id").text = student_id
        ET.SubElement(student, "last_name").text = last_name
        ET.SubElement(student, "first_name").text = first_name
        ET.SubElement(student, "birth_year").text = str(birth_year)
        ET.SubElement(student, "course").text = str(course)

        # Add grades
        grades_elem = ET.SubElement(student, "grades")
        for i, grade in enumerate(grades, 1):
            ET.SubElement(grades_elem, f"exam{i}").text = str(grade)

        self.save()
        return student

    def find_student(self, student_id):
        for student in self.root.findall(".//student"):
            if student.find("id").text == student_id:
                return student
        return None

    def delete_student(self, student_id):
        student = self.find_student(student_id)
        if student is None:
            raise ValueError(f"Student with ID {student_id} not found")

        self.root.remove(student)
        self.save()

    def edit_student(self, student_id, last_name=None, first_name=None,
                     birth_year=None, course=None, grades=None):
        student = self.find_student(student_id)
        if student is None:
            raise ValueError(f"Student with ID {student_id} not found")

        if last_name:
            student.find("last_name").text = last_name
        if first_name:
            student.find("first_name").text = first_name
        if birth_year:
            student.find("birth_year").text = str(birth_year)
        if course:
            student.find("course").text = str(course)
        if grades:
            grades_elem = student.find("grades")
            for i, grade in enumerate(grades, 1):
                grades_elem.find(f"exam{i}").text = str(grade)

        self.save()

    def calculate_average(self, student):
        grades = []
        for exam in student.find("grades").findall("*"):
            grades.append(int(exam.text))
        return mean(grades)

    def calculate_scholarships(self, output_format='xml'):
        # Calculate average for all students
        students_data = []
        for student in self.root.findall(".//student"):
            avg_grade = self.calculate_average(student)
            all_grades = [int(exam.text) for exam in student.find("grades").findall("*")]

            # Check if all grades are above 51
            if all(grade > 51 for grade in all_grades):
                students_data.append({
                    'id': student.find("id").text,
                    'last_name': student.find("last_name").text,
                    'first_name': student.find("first_name").text,
                    'birth_year': student.find("birth_year").text,
                    'course': student.find("course").text,
                    'average_grade': avg_grade,
                    'grades': all_grades,
                    'increased': all(grade > 90 for grade in all_grades)
                })

        # Sort by average grade in descending order
        students_data.sort(key=lambda x: x['average_grade'], reverse=True)

        # Take top 40% of students
        scholarship_count = max(1, int(len(students_data) * 0.4))
        scholarship_students = students_data[:scholarship_count]

        # Write to output file based on format
        if output_format.lower() == 'xml':
            self._write_scholarships_xml(scholarship_students, 'scholarships.xml')
        else:  # json
            self._write_scholarships_json(scholarship_students, 'scholarships.json')

    def _write_scholarships_xml(self, students, output_file):
        root = ET.Element("scholarships")

        for student in students:
            student_elem = ET.SubElement(root, "student")
            ET.SubElement(student_elem, "id").text = student['id']
            ET.SubElement(student_elem, "last_name").text = student['last_name']
            ET.SubElement(student_elem, "first_name").text = student['first_name']
            ET.SubElement(student_elem, "birth_year").text = student['birth_year']
            ET.SubElement(student_elem, "course").text = student['course']
            ET.SubElement(student_elem, "average_grade").text = str(student['average_grade'])
            ET.SubElement(student_elem, "increased").text = str(student['increased']).lower()

        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

    def _write_scholarships_json(self, students, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"scholarships": students}, f, ensure_ascii=False, indent=4)


manager = StudentManager('students.xml')
manager.add_student('1', 'Петренко', 'Іван', 2002, 3, [85, 92, 78, 94])
manager.add_student('2', 'Іваненко', 'Марія', 2003, 2, [95, 91, 98, 92])
manager.add_student('3', 'Сидоренко', 'Олег', 2001, 4, [65, 72, 68, 70])
manager.calculate_scholarships(output_format='xml')