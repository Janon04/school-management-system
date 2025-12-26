"""
Decorators for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles=[]):
    """
    Decorator to restrict access to views based on user role
    Usage: @role_required(['ADMIN', 'TEACHER'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
        
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to restrict access to admin users only"""
    return role_required(['ADMIN'])(view_func)


def teacher_required(view_func):
    """Decorator to restrict access to teachers"""
    return role_required(['ADMIN', 'TEACHER'])(view_func)


def student_required(view_func):
    """Decorator to restrict access to students"""
    return role_required(['ADMIN', 'STUDENT'])(view_func)


def parent_required(view_func):
    """Decorator to restrict access to parents"""
    return role_required(['ADMIN', 'PARENT'])(view_func)
