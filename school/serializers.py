from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
from .models import Course, Teacher, CourseTeacherRelationship, User, Rate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['id', 'name']

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'name']

class CourseTeacherRelationshipSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    course_id = serializers.CharField(write_only=True)
    teacher_id = serializers.CharField(write_only=True)

    class Meta:
        model = CourseTeacherRelationship
        fields = ['id', 'course', 'teacher', 'year', 'semester']

class ModuleSerializer(serializers.Serializer):
    course = CourseSerializer(read_only=True)
    year = serializers.IntegerField()
    semester = serializers.CharField()
    teachers = TeacherSerializer(many=True, read_only=True)
    
class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = User.objects.filter(username=username).first()
            
            if user:
                if not user.check_password(password):
                    raise serializers.ValidationError("Password error")
            else:
                raise serializers.ValidationError("user does not exist")
        else:
            raise serializers.ValidationError("Username and password must be provided")
            
        attrs['user'] = user
        return attrs

class RateSerializer(serializers.ModelSerializer):
    teacher_id = serializers.CharField(write_only=True)
    course_id = serializers.CharField(write_only=True)
    year = serializers.IntegerField(write_only=True)
    semester = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        model = Rate
        fields = [
            'id', 'rate', 'teacher_id', 'course_id', 
            'year', 'semester', 'token'
        ]

    def validate(self, data):
        try:
            token = Token.objects.get(key=data['token'])
            user = token.user
            if not user.is_active:
                raise AuthenticationFailed('User inactive or deleted.')
            data['user'] = user
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token.')

        try:
            course_teacher = CourseTeacherRelationship.objects.get(
                teacher_id=data['teacher_id'],
                course_id=data['course_id'],
                year=data['year'],
                semester=data['semester']
            )
            data['course_teacher'] = course_teacher
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Wrong information of course or teacher.")
        return data

    def create(self, validated_data):
        validated_data.pop('teacher_id')
        validated_data.pop('course_id')
        validated_data.pop('year')
        validated_data.pop('semester')
        validated_data.pop('token')

        try:
            rate = Rate.objects.get(
                courseTeacher=validated_data['course_teacher'],
                user=validated_data['user']
            )
            raise serializers.ValidationError({"non_field_errors": ["You had already rate it."]})
        except ObjectDoesNotExist:
            rate = Rate.objects.create(
            courseTeacher=validated_data['course_teacher'],
            user=validated_data['user'],
            rate=validated_data['rate']
            )
            return rate
        
class TeacherRateAverageSerializer(serializers.Serializer):
    teacher_id = serializers.CharField()
    teacher_name = serializers.CharField()
    average_rate = serializers.FloatField()

class EasyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['id', 'user', 'rate', 'courseTeacher']

class CourseTeacherRateAverageSerializer(serializers.Serializer):
    teacher_name = serializers.CharField()
    course_name = serializers.CharField()
    average_rate = serializers.FloatField()