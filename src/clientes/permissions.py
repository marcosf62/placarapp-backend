from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Permite consultar las reseñas, pero solamente
    su propietario puede modificarlas o eliminarlas.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.cliente.usuario == request.user
