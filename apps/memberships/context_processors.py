from django.utils import timezone


def membership_context(request):
    """Inject membership info into every template."""
    context = {}
    if request.user.is_authenticated:
        context['user_membership'] = request.user.active_membership
    return context
