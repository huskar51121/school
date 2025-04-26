from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
class Course(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CourseTeacherRelationship(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, to_field='id', on_delete=models.CASCADE, related_name='relationships')
    teacher = models.ForeignKey(Teacher, to_field='id', on_delete=models.CASCADE, related_name='relationships')
    year = models.IntegerField()
    semester = models.CharField(max_length=20)

    class Meta:
        unique_together = [('course', 'teacher', 'year', 'semester')]

    def __str__(self):
        return f"{self.course.name} - {self.teacher.name} ({self.year}, {self.semester})"
    
class Rate(models.Model):
    id = models.AutoField(primary_key=True)
    courseTeacher = models.ForeignKey(CourseTeacherRelationship, to_field='id', on_delete=models.CASCADE, related_name='ct_relationships')
    user = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE, related_name='user_relationships')
    rate = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    class Meta:
        unique_together = [('courseTeacher', 'user')]
    def __str__(self):
        return f"user: {self.user} rate: {self.rate} information: {self.courseTeacher.id})"
