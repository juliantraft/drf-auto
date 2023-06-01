import argparse
import ast
import os


parser = argparse.ArgumentParser(
                    formatter_class=argparse.RawTextHelpFormatter,
                    prog='python auto-drf.py',
                    description='''Simple DRF API Creation Tool
Generates all files by default.

Example (generate serializers only):
python auto-drf.py models.py -s''')

parser.add_argument('models_file', help='file name (models.py)')
parser.add_argument("-s", "--serializer"  , action='store_true', help="generate serializers.py")
parser.add_argument("-v", "--viewset"  , action='store_true', help="generate views.py")
parser.add_argument("-p", "--path"  , action='store_true', help="generate urls.py")

args = parser.parse_args()


with open(args.models_file) as file:
    node = ast.parse(file.read())
    models = [x for x in node.body if isinstance(x, ast.ClassDef)]


def get_table(model):

    for node in model.body:
        if isinstance(node, ast.ClassDef) and (node.name == 'Meta'):
            meta = node
            break

    for node in meta.body:
        if (node.targets[0].id == 'db_table'):
            return node.value.value



def serializer_generator(models):
    filename = 'serializers.py'
    if os.path.exists(filename):
        os.remove(filename)

    file = open(filename, 'w')
    file.write(f"""from rest_framework import serializers

from .models import (\n""")
    
    for model in models:
        m = f"    {model.name},\n"
        file.write(m)

    file.write(")\n\n")

    for model in models:
        serializer =f"""class {model.name}Serializer(serializers.ModelSerializer):

    class Meta:
        model = {model.name}
        fields = '__all__'

"""
        file.write(serializer)
    file.close



def viewset_generator(models):
    filename = 'views.py'
    if os.path.exists(filename):
        os.remove(filename)

    file = open(filename, 'w')

    file.write("""from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import (\n""")

    for model in models:
        m = f"    {model.name},\n"
        file.write(m)

    file.write(")\n\nfrom .serializers import (\n")

    for model in models:
        serializer = f"    {model.name}Serializer,\n"
        file.write(serializer)

    file.write(")\n\n")

    for model in models:
        table = get_table(model)
        viewset =f"""class {model.name}ViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    @extend_schema(
        description = \"""Tabel: {table}
Kelengkapan Data: Lengkap\""",
        responses={{200: {model.name}Serializer(many=True)}},
    )
    @action(detail=True, methods=["get"])
    def list(self,request):
        queryset = {model.name}.objects.all()
        serializer = {model.name}Serializer(queryset, many=True)
        return Response({{"count": len(queryset), "data": serializer.data}})


"""
        file.write(viewset)
    file.close()



def path_generator(models):
    filename = 'urls.py'
    if os.path.exists(filename):
        os.remove(filename)

    file = open(filename, 'w')
    file.write("from .views import (\n")

    for model in models:
        viewset = f"    {model.name}ViewSet,\n"
        file.write(viewset)
    file.write(")\n\nfrom django.urls import path\n\nurl_patterns = [\n")

    for model in models:
        table = get_table(model)
        path = f"    path('{table}/', {model.name}ViewSet.as_view({{'get':'list'}})),\n"
        file.write(path)

    file.write("]")
    file.close()


if not (args.serializer or args.viewset or args.path):
    serializer_generator(models)
    viewset_generator(models)
    path_generator(models)  
else:
    if args.serializer:
        serializer_generator(models)
    if args.viewset:
        viewset_generator(models)
    if args.path:
        path_generator(models)
