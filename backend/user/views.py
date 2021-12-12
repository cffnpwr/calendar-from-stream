from rest_framework import generics, permissions, status
from rest_framework.response import Response

from user.serializer import UserSerializer
from user.models import User


class UserView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        self.lookup_field = 'id'
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if serializer.data['id'] == request.user.id:

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        self.lookup_field = 'id'
        instance = self.get_object()

        if self.get_serializer(instance).data['id'] == request.user.id:
            serializer = self.get_serializer(instance, data=request.data)

            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_403_FORBIDDEN)
