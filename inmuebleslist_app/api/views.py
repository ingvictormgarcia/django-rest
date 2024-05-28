from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from inmuebleslist_app.models import Inmueble, Empresa, Comentario
from inmuebleslist_app.api.serializers import InmuebleSerializer, EmpresaSerializer, ComentarioSerializer
# from rest_framework.decorators import api_view
from rest_framework import status, generics, mixins
from rest_framework.views import APIView
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from inmuebleslist_app.api.permissions import IsAdminOrReadOnly, IsComentarioUserOrReadOnly
from rest_framework.throttling import (UserRateThrottle, 
AnonRateThrottle, ScopedRateThrottle)
from inmuebleslist_app.api.throttling import ComentarioCreateThrottle, ComentarioListThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from inmuebleslist_app.api.pagination import InmueblePagination, InmuebleLOPagination
# Create your views here.

class UsuarioComentario(generics.ListAPIView):
    serializer_class = ComentarioSerializer
    def get_queryset(self):
        username = self.kwargs['username']
        return Comentario.objects.filter(comentario_user__username=username)

class ComentarioCreate(generics.CreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ComentarioCreateThrottle]
    def get_queryset(self):
        return Comentario.objects.all()
    
    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        inmueble = Inmueble.objects.get(pk=pk)
        user = self.request.user
        comentario_queryset = Comentario.objects.filter(inmueble=inmueble, comentario_user=user)
        if comentario_queryset.exists():
            raise ValidationError('El usuario ya realizo un comentario en este inmueble')  
        if inmueble.number_calificacion == 0:
            inmueble.avg_calificacion = serializer.validated_data['calificacion']
        else:
            inmueble.avg_calificacion = (serializer.validated_data['calificacion']
                                         + inmueble.avg_calificacion) / 2
        inmueble.number_calificacion = inmueble.number_calificacion + 1
        inmueble.save()    
        
        serializer.save(inmueble=inmueble, comentario_user=user)
    

class ComentarioList(generics.ListCreateAPIView):
    # queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    # permission_classes = [IsAuthenticated]
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]
    throttle_classes = [ComentarioListThrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['comentario_user__username', 'active']
    
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Comentario.objects.filter(inmueble=pk)

class ComentarioDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer
    permission_classes = [IsComentarioUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'comentario-detail'

# class ComentarioList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
    
#     def post(self, request, *args, **Kwargs):
#         return self.create(request, *args, **Kwargs)
    
# class ComentarioDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
#     queryset = Comentario.objects.all()
#     serializer_class = ComentarioSerializer
    
#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

class EmpresaVS(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminOrReadOnly]
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
        
# class EmpresaVS(viewsets.ViewSet):
#     def list(self, request):
#         queryset = Empresa.objects.all()
#         serializer = EmpresaSerializer(queryset, many=True)
#         return Response(serializer.data)  
    
#     def retrieve(self, request, pk=None):
#         queryset = Empresa.objects.all()
#         inmueblelist = get_object_or_404(queryset, pk=pk)
#         serializer = EmpresaSerializer(inmueblelist)
#         return Response(serializer.data)
    
#     def create(self, request):
#         serializer = EmpresaSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def update(self, request, pk):
#         try:
#             empresa = Empresa.objects.get(pk=pk)
#         except Empresa.DoesNotExist:
#             return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = EmpresaSerializer(empresa, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
#     def destroy(self, request, pk):
#         try:
#             empresa = Empresa.objects.get(pk=pk)
#         except Empresa.DoesNotExist:
#             return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
#         empresa.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)    

class EmpresaAV(APIView):
    def get(self, request):
        empresas = Empresa.objects.all()
        serializer = EmpresaSerializer(empresas, many=True, context={'request':request})
        return Response(serializer.data)
    
    def post(self, request):
        serializer = EmpresaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class EmpresaDetalleAV(APIView):
    def get(self, request, pk):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa no encontrada' }, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpresaSerializer(empresa, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa no encontrada' }, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpresaSerializer(empresa, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        try:
            empresa = Empresa.objects.get(pk=pk)
        except Empresa.DoesNotExist:
            return Response({'error': 'Empresa no encontrada' }, status=status.HTTP_404_NOT_FOUND)
        empresa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class InmuebleList(generics.ListAPIView):
    queryset = Inmueble.objects.all()
    serializer_class = InmuebleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['direccion', 'empresa__nombre']
    pagination_class = InmueblePagination
    # pagination_class = InmuebleLOPagination
        
class InmuebleListAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def get(self, request):
        inmueble = Inmueble.objects.all()
        serializer = InmuebleSerializer(inmueble, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = InmuebleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else: 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class InmuebleDetalleAV(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def get(self, request, pk):
        try:
            inmueble = Inmueble.objects.get(pk=pk)
        except Inmueble.DoesNotExist:
            return Response({'Error': 'Inmueble no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = InmuebleSerializer(inmueble)
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            inmueble = Inmueble.objects.get(pk=pk)
        except Inmueble.DoesNotExist:
            return Response({'Error': 'Inmueble no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        de_serializer = InmuebleSerializer(inmueble, data=request.data)
        if de_serializer.is_valid():
            de_serializer.save()
            return Response(de_serializer.data)
        else:
            return Response(de_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            inmueble = Inmueble.objects.get(pk=pk)
            inmueble.delete()
        except Inmueble.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)    

# @api_view(['GET', 'POST'])
# def inmueble_list(request):
#     if request.method == 'GET':
#         inmuebles = Inmueble.objects.all()
#         serializer = InmuebleSerializer(inmuebles, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         de_serializer = InmuebleSerializer(data=request.data)
#         if de_serializer.is_valid():
#             de_serializer.save()
#             return Response(de_serializer.data)
#         else:
#             return Response(de_serializer.errors)

# @api_view(['GET', 'PUT', 'DELETE'])
# def inmueble_detalle(request, pk):
#     try:
#         if request.method == 'GET':
#             inmueble = Inmueble.objects.get(pk=pk)
#             serializer = InmuebleSerializer(inmueble)
#             return Response(serializer.data)
#     except Inmueble.DoesNotExist:
#         return Response({'Error': 'No existe'}, status=status.HTTP_404_NOT_FOUND)
        
#     if request.method == 'PUT':
#         inmueble = Inmueble.objects.get(pk=pk)
#         de_serializer = InmuebleSerializer(inmueble, data=request.data)
#         if de_serializer.is_valid():
#             de_serializer.save()
#             return Response(de_serializer.data)
#         else:
#             return Response(de_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
#     if request.method == 'DELETE':
#         try:
#             inmueble = Inmueble.objects.get(pk=pk)
#             inmueble.delete()
#         except Inmueble.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         return Response(status=status.HTTP_204_NO_CONTENT)
    