from rest_framework.throttling import SimpleRateThrottle


class AlertEmailRateThrottle(SimpleRateThrottle):
    scope = "alert_email"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class QuestionSubmitRateThrottle(SimpleRateThrottle):
    scope = "question_submit"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class CVBuilderSubmitRateThrottle(SimpleRateThrottle):
    scope = "cv_builder_submit"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
