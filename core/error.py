from django.shortcuts import render

def page_not_found(request, exception):
    """_summary_
    Handle a 404 response

    Args:
        request (_type_): _description_
        exception (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(request, 'home/page-404.html', status=404)


def server_error(request):
    """_summary_
    Handle a 500 response

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(request, 'home/page-500.html', status=500)


def permission_denied(request, exception):
    """_summary_
    Handle a 403 response

    Args:
        request (_type_): _description_
        exception (_type_): _description_

    Returns:
        _type_: _description_
    """
    return render(request, 'home/page-403.html', status=403)