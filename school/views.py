from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from .serializers import *
from collections import defaultdict
from django.db.models import Avg, Count,F
from django.shortcuts import get_object_or_404

class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "注册成功",
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # 获取用户的Token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "登录成功",
                "token": token.key,
                "username": user.username
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ModuleView(APIView):
    def get(self, request):
        relationships = CourseTeacherRelationship.objects.select_related('course', 'teacher').all()
        grouped = defaultdict(lambda: {'course': None, 'year': None, 'semester': None, 'teachers': []})

        for rel in relationships:
            key = (rel.course.id, rel.year, rel.semester)
            if grouped[key]['course'] is None:
                grouped[key]['course'] = rel.course
                grouped[key]['year'] = rel.year
                grouped[key]['semester'] = rel.semester
            grouped[key]['teachers'].append(rel.teacher)
        modules = list(grouped.values())
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RateView(APIView):
    def get(self, request):
        queryset = Rate.objects.select_related('courseTeacher__teacher').values(
            'courseTeacher__teacher__id',
            'courseTeacher__teacher__name'
        ).annotate(
            average_rate=Avg('rate')
        ).order_by('courseTeacher__teacher__id')
        
        data = [{
            'teacher_id': item['courseTeacher__teacher__id'],
            'teacher_name': item['courseTeacher__teacher__name'],
            'average_rate': item['average_rate']
        } for item in queryset]
        
        serializer = TeacherRateAverageSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = RateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Rate is created",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CourseTeacherRateView(APIView):
    def get(self, request):
        teacher_id = request.query_params.get('teacher_id')
        course_id = request.query_params.get('course_id')
        print(teacher_id)
        print(course_id)
        
        # 先通过CourseTeacherRelationship找到所有的ct，再代入到Rate中
        relationship = get_object_or_404(
            CourseTeacherRelationship,
            teacher_id=teacher_id,
            course_id=course_id
        )
        
        rates = Rate.objects.filter(courseTeacher=relationship)
        
        average_rate = rates.aggregate(avg_rate=Avg('rate'))['avg_rate'] or 0
        
        data = {
            'teacher_name': relationship.teacher.id,
            'course_name': relationship.course.name,
            'average_rate': round(average_rate, 2)
        }
        
        serializer = CourseTeacherRateAverageSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)