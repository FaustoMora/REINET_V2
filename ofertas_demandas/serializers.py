# -*- encoding: utf-8 -*-

from datetime import date, datetime
from ofertas_demandas.models import DiagramaPorter, DiagramaBusinessCanvas, Oferta, MiembroEquipo
from usuarios.models import Perfil

__author__ = 'rbalda'


from rest_framework.serializers import ModelSerializer

def crear_codigo(nombre_oferta):
    nombre_oferta.replace(' ','-')
    return '%s-%s'%(nombre_oferta,datetime.now().strftime("%Y-%m-%d-%H-%M"))


class DiagramaPorterSerializador(ModelSerializer):
    class Meta:
        model = DiagramaPorter
        fields = ('id_diagrama_porter','competidores','sustitutos','consumidores','proveedores','nuevosMiembros')
        read_only_fields = ('id_diagrama_porter',)


class DiagramaBusinessCanvasSerializador(ModelSerializer):
    class Meta:
        model = DiagramaBusinessCanvas
        fields = ('id_diagrama_business_canvas','asociaciones_clave','actividades_clave','recursos_clave','propuesta_valor',
                  'relacion_clientes','canales_distribucion','segmento_mercado','estructura_costos','fuente_ingresos')
        read_only_fields = ('id_diagrama_canvas',)


class OfertaSerializador(ModelSerializer):
    fk_diagrama_competidores = DiagramaPorterSerializador(required=False,allow_null=True)
    fk_diagrama_canvas = DiagramaBusinessCanvasSerializador(required=False,allow_null=True)

    class Meta:
        model = Oferta
        fields = (
            'codigo','tipo','nombre','publicada','calificacion_total','descripcion','dominio','subdominio',
            'fecha_creacion','fecha_publicacion','tiempo_para_estar_disponible','perfil_beneficiario','perfil_cliente',
            'descripcion_soluciones_existentes','estado_propieada_intelectual','evidencia_traccion','cuadro_tendencias_relevantes',
            'equipo','palabras_clave','comentarios','alcance','fk_diagrama_competidores','fk_diagrama_canvas')

        read_only_fields = ('id_oferta','codigo','fecha_publicacion','fecha_creacion',
                            'calificacion_total','palabras_clave','comentarios','alcance')

    def create(self,validated_data):
        diagrama_competidores = validated_data.pop('fk_diagrama_competidores',None)
        diagrama_canvas = validated_data.pop('fk_diagrama_canvas',None)
        diagrama_canvas_exist = False
        competidores_canvas_exist = False

        canvas=None
        porter = None

        for d in diagrama_canvas:
            if not diagrama_canvas[d]==u'':
                diagrama_canvas_exist = True

        for d in diagrama_competidores:
            if not diagrama_competidores[d]=='':
                competidores_canvas_exist = True

        if(competidores_canvas_exist):
           canvas = DiagramaBusinessCanvas.objects.create(**diagrama_canvas)
        if(diagrama_canvas_exist):
            porter = DiagramaPorter.objects.create(**diagrama_competidores)

        nombre = validated_data['nombre']
        oferta = Oferta.objects.create(fk_diagrama_competidores=porter,fk_diagrama_canvas=canvas,codigo=crear_codigo(nombre),**validated_data)
        MiembroEquipo.objects.create(fk_participante=Perfil.objects.get(id=self.context['request'].user.id),fk_oferta_en_que_participa=oferta,
                                     es_propietario=True,rol_participante='dueño de la oferta',estado_membresia=1,activo = True)

        return oferta

