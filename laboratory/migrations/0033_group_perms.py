# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-28 14:49
from __future__ import unicode_literals

from django.db import migrations

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from django.db import migrations


def set_perms(group,perms):
    if not hasattr(perms,'__iter__'):
         group.permissions.add(perms)
    else:
         for perm in perms:
            group.permissions.add(perm)
    
    
def load_group_perms(apps, schema_editor):
  
    perms_student =[ # reservations
        "add_reservation","view_reservation",
        ]
    
    perms_professor = [  # reservations
        "add_reservation","view_reservation",
        # Procedure
        "view_procedure","view_procedurestep","view_procedurerequiredobject","view_procedureobservations",
        # procedureobservations
        "add_procedureobservations","change_procedureobservations","delete_procedureobservations",
        # procedure
        "add_procedure","change_procedure","delete_procedure",
        # procedurestep
        "add_procedurestep", "change_procedurestep","delete_procedurestep",
        # procedurerequiredobject
        "add_procedurerequiredobject","change_procedurerequiredobject", "delete_procedurerequiredobject",
        
        # solutions
        "add_solution","change_solution",
        ]
        
    perms_laboratory = [ # reservations
        "add_reservation","change_reservation","delete_reservation","add_reservationtoken",
        "change_reservationtoken","delete_reservationtoken","view_reservation",
        
        # objets 
        "add_shelfobject","change_shelfobject","delete_shelfobject",
        "add_object","change_object","delete_object",
        
        # objectfeatures        
        "add_objectfeatures",        "change_objectfeatures","delete_objectfeatures",
        
        # procedurerequiredobject
        "view_procedurerequiredobject",
        "add_procedurerequiredobject","change_procedurerequiredobject","delete_procedurerequiredobject",
        
        # furniture
        "add_furniture","change_furniture","delete_furniture",
        
        # laboratory
        "add_laboratoryroom","change_laboratoryroom","delete_laboratoryroom",

        #Prodcuts
        "add_product","change_product","delete_product",
        
        #onsertation
        "add_observation","change_observation","delete_observation",
       
        #CL Inventory
        "add_clinventory","change_clinventory","delete_clinventory","add_solution",

        # solutions
        "add_solution","change_solution","delete_solution",


        ]

        
    GLaboratory = Group.objects.get(name='Laboratory Administrator')
    if not GLaboratory:
        GLaboratory = Group(name='Laboratory Administrator')
        GLaboratory.save()
     
    GProfessor = Group.objects.get(name='Professor')
    if not GProfessor:   
        GProfessor = Group(name='Professor')
        GProfessor.save()
        
    GStudent = Group.objects.get(name='Student')
    if not GStudent:     
        GStudent = Group(name='Student')
        GStudent.save()
 
    
    # add perms to student
    # puede ver y hacer reservaciones
    perms = Permission.objects.filter(codename__in=perms_student)
    set_perms(GStudent,perms)
    
    # add perms to Professor
    # 1. Puede hacer reservaciones
    # 2. Puede administrar procedientos
    # (3). No aprueba reservaciones
    # 4. Puede calcular soluciones
    perms = Permission.objects.filter(codename__in=perms_professor)
    set_perms(GProfessor,perms)   
    # add perms to Laboratories Administrator    
    # 1. Puede administrar reservaciones
    # 2. Agregar Objectos
    # 3. Agregar stantes
    # 4. Administrar estructura de lab
    perms=Permission.objects.filter(codename__in=perms_laboratory)
    set_perms(GLaboratory,perms)   
    


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0032_auto_20180216_1502'),
    ]

    operations = [
         migrations.RunPython(load_group_perms),
    ]
