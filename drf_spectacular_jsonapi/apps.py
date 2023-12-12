from django.apps import AppConfig


class DRFSpectacularJsonApiConfig(AppConfig):
    name = 'drf_spectacular_jsonapi'
    verbose_name = "drf-spectacular-jsonapi"

    def ready(self):
        import drf_spectacular_jsonapi.openapi  # noqa: F408
