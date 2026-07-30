from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_redis import get_redis_connection
from django.contrib.auth import get_user_model
from .serializer import ScoreUpInputSerializer, ScoreUpOutputSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

User = get_user_model()
redis_conn = get_redis_connection('default')

class LeaderBoardView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get(self, request):
        raw_data = redis_conn.zrevrange('leaderboard', 0, 9, withscores=True)
        userId = [int(uid.decode('utf-8')) for uid in raw_data]

        users_queryset = User.objects.filter(id__in=userId).values('id', 'first_name', 'last_name')
        users_dict = {u['id']: f"{u['first_name']} {u['last_name']}" for u in users_queryset}

        leaderboard = []
        for i, (uid_bytes ,score) in enumerate(raw_data):
            u_id = int(uid_bytes.decode('utf-8'))
            leaderboard.append({
                "rank": i+1,
                "user_id":  u_id,
                "fullname": users_dict.get(u_id, "No'malum foydalanuvchi"),
                "score": int(score)
            })

class ScoreUpView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request):
        user_id = request.data.get('user_id')
        points_earned = request.data.get('points_earned')

        if not user_id or not points_earned:
            return Response({"error": "kerakli maydonlar to`ldirilishi shart"})
        
        try:
            new_score = redis_conn.zincrby('leaderboard', points_earned, str(user_id))
            
            user_obj = User.objects.filter(id=user_id).first()
            full_name = f"{user_obj.first_name} {user_obj.last_name}" if user_obj else "No'malum"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'leaderboard_group',
                {
                    'type': 'leaderboard_update_message',
                    'message': {
                        'user_id': int(user_id),
                        'full_name': full_name,
                        'new_score': int(new_score)
                    }
                }
            )   
            return Response({
                "success": True,
                "message": "Ball yangilandi",
                "new_score": int(new_score)
            })
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        
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