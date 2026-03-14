import sentry_sdk
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def sentry_debug(request):
    error_type = request.GET.get("type", "exception")
    if error_type == "exception":
        raise Exception(
            "Sentry test exception — triggered manually from /sentry-debug/"
        )
    elif error_type == "zero":
        result = 1 / 0  # noqa
    elif error_type == "capture":
        sentry_sdk.capture_message(
            "Sentry test message from /sentry-debug/", level="error"
        )
        return HttpResponse("✅ Sentry message captured — check your Sentry dashboard.")
    return HttpResponse("Done")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("todo.urls")),
    path("", include("django_prometheus.urls")),
    path("sentry-debug/", sentry_debug, name="sentry_debug"),
]
