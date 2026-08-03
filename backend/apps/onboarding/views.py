from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import OnboardingState
from .serializers import OnboardingStateSerializer
from apps.stores.models import Store


class OnboardingStateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state, _ = OnboardingState.objects.get_or_create(user=request.user)
        return Response(OnboardingStateSerializer(state).data)

    def post(self, request):
        state, _ = OnboardingState.objects.get_or_create(user=request.user)
        step = request.data.get("step")
        
        if step is not None:
            try:
                step = int(step)
            except ValueError:
                return Response({"error": "Invalid step"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Enforce Step 2 completion only if a store is connected
            if step > 2:
                has_store = Store.objects.filter(owner=request.user, status=Store.Status.CONNECTED).exists()
                if not has_store:
                    return Response({"error": "You must connect a store before advancing past Step 2."}, status=status.HTTP_403_FORBIDDEN)
                    
            state.current_step = step
            state.save()
            
        return Response(OnboardingStateSerializer(state).data)
