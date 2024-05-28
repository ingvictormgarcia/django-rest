from rest_framework import serializers
from inmuebleslist_app.models import Inmueble, Empresa, Comentario
      
class ComentarioSerializer(serializers.ModelSerializer):
    comentario_user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comentario
        exclude = ['inmueble']
        # fields = '__all__'
        

class InmuebleSerializer(serializers.ModelSerializer):
    # longitud_direccion = serializers.SerializerMethodField()
    comentarios = ComentarioSerializer(many=True, read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre')
    class Meta:
        model = Inmueble
        fields = "__all__"
        # fields = ['id', 'pais', 'imagen']
        # exclude = ['id']
        
        
# class EmpresaSerializer(serializers.HyperlinkedModelSerializer):
class EmpresaSerializer(serializers.ModelSerializer):
    inmueblelist = InmuebleSerializer(many=True, read_only=True)
    # inmueblelist = serializers.StringRelatedField(many=True)
    # inmueblelist = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # inmueblelist = serializers.HyperlinkedIdentityField(
    #     many=True, 
    #     read_only=True,
    #     view_name='inmueble_detalle')
    class Meta:
        model = Empresa
        fields = "__all__"  
        
        
        
    # def get_longitud_direccion(self, object):
    #     cantidad_caracteres = len(object.direccion)
    #     return cantidad_caracteres
        
    # def validate(self, data):
    #     if data['direccion']==data['pais']:
    #         raise serializers.ValidationError('La direccion y pais no deben ser iguales')
    #     else:
    #         return data

# def column_longitud(value):
#     if len(value) < 2:
#         raise serializers.ValidationError('La direccion es demasiado corta')

# class InmuebleSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     direccion = serializers.CharField(validators=[column_longitud])
#     pais = serializers.CharField()
#     descripcion = serializers.CharField()
#     imagen = serializers.CharField()
#     active = serializers.BooleanField() 
    
#     def create(self, validate_data):
#         return Inmueble.objects.create(**validate_data)
    
#     def update(self, instance, validated_data):
#         instance.direccion = validated_data.get('direccion', instance.direccion)
#         instance.pais = validated_data.get('pais', instance.pais)
#         instance.descripcion = validated_data.get('descripcion', instance.descripcion)
#         instance.imagen = validated_data.get('imagen', instance.imagen)
#         instance.active = validated_data.get('active', instance.active)
#         instance.save()
#         return instance
    
#     def validate(self, data):
#         if data['direccion']==data['pais']:
#             raise serializers.ValidationError('La direccion y pais no deben ser iguales')
#         else:
#             return data