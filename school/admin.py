from django.contrib import admin  
from .models import Teacher, Course, CourseTeacherRelationship, User, Rate

admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(CourseTeacherRelationship)
admin.site.register(Rate)