from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import Group
from .models import CustomUser
from .forms import CustomUserCreationForm  # Asegúrate de tener un formulario para CustomUser

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Agregar automáticamente al grupo Docente
            grupo_docente, created = Group.objects.get_or_create(name='Docente')
            usuario.groups.add(grupo_docente)
            login(request, usuario)
            return redirect('inicio')  # Cambia 'inicio' por tu vista principal
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/Authentication/signup.html', {'form': form})