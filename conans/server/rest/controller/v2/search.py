from bottle import request

from conans.model.recipe_ref import RecipeReference
from conans.server.rest.bottle_routes import BottleRoutes
from conans.server.service.v2.search import SearchService


class SearchControllerV2(object):
    """
        Serve requests related with Conan
    """
    @staticmethod
    def attach_to(app):

        r = BottleRoutes()

        @app.route(r.common_search, method=["GET"])
        def search(auth_user):
            pattern = request.params.get("q", None)
            ignore_case = request.params.get("ignorecase", True)
            if isinstance(ignore_case, str):
                ignore_case = 'false' != ignore_case.lower()
            search_service = SearchService(app.authorizer, app.server_store, auth_user)
            references = [repr(ref) for ref in search_service.search(pattern, ignore_case)]
            return {"results": references}

        @app.route(r.common_search_packages, method=["GET"])
        @app.route(r.common_search_packages_revision, method=["GET"])
        def search_packages(name, version, username, channel, auth_user, revision=None):
            query = request.params.get("q", None)
            search_service = SearchService(app.authorizer, app.server_store, auth_user)
            ref = RecipeReference(name, version, username, channel, revision)
            info = search_service.search_packages(ref, query)
            return info
