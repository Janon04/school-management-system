"""
Views for Parent Management
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Parent


@login_required
def parent_list_view(request):
    """List all active parents"""
    parents = Parent.objects.filter(is_active=True).select_related('user')
    return render(request, 'parents/parent_list.html', {'parents': parents})


@login_required
def parent_detail_view(request, pk):
    """View parent details"""
    parent = get_object_or_404(Parent, pk=pk)
    children = parent.children.filter(is_active=True)
    
    context = {
        'parent': parent,
        'children': children,
    }
    return render(request, 'parents/parent_detail.html', context)
