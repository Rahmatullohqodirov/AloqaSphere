from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_redis import get_redis_connection
from django.contrib.auth import get_user_model
from .serializer import ScoreUpInputSerializer, ScoreUpOutputSerializer
import json

User = get_user_model()
redis_conn = get_redis_connection('default')

class LeaderBoardView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get(self,request):
        raw_data = redis_conn.zrevrange("leaderboard", 0,9, withscores=True)
        
        userID = [int(user_id_bytes.decode("utf-8")) for user_id_bytes, _ in raw_data]
        users_queryset = User.objects.filter(id__in=userID).values('id', 'first_name', 'last_name')
        users_dict = {u['id']: f"{u['first_name']} {u['last_name']}" for u in users_queryset}

        leaderboard = []
        for i, (user_id_bytes, score) in enumerate(raw_data):
            u_id = int(user_id_bytes.decode('utf-8'))
            fullname = users_dict.get(u_id, "Noma'lum foydalanuvchi")

            leaderboard.append({
                "rank": i + 1,
                "user_id": u_id,
                "full_name": fullname,
                "score": int(score)
            })
        return Response({
            "success": True,
            "leaderboard": leaderboard
        }, status=200)

class ScoreUpView(APIView):
    serializer_class = ScoreUpInputSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    def post(self, request):
        serializer = ScoreUpInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        user_id = serializer.validated_data["user_id"]
        points_earned = serializer.validated_data["points_earned"]
        new_score = redis_conn.zincrby("leaderboard", points_earned, str(user_id))
        return Response({
            "success": True,
            "message": "Ball muvaffaqiyatli yangilandi",
            "new_score": int(new_score)
        }, status=200)
        

class DashboardView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    def get(self, request):
        total_registered_users = User.objects.count()
        total_active_leaderboard =  redis_conn.zcard("leaderboard")

        return Response({
            "success": True,
            "data": {
                "total_registered_users": total_registered_users,
                "active_in_leaderboard": total_active_leaderboard,
                "status": "Active"
            }
        }, status=200)