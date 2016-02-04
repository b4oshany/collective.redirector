from datetime import datetime

from plone.app.layout.viewlets import ViewletBase
from plone import api
from zope.component import ComponentLookupError
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getMultiAdapter
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.api.exc import InvalidParameterError
from collective.redirectpage.interfaces import (IRedirectPage, schema_prefix,
                                                TESTDATA)

from time import time
from plone.memoize import ram


class JSFunctionsViewlet(ViewletBase):
	pass


class RedirectViewlet(ViewletBase):
    """ viewlet that displays announcements """

    def script(self, obj):
        return "<script>$(document).ready(function(){url_redirector('%s', '%s', '%s');});</script>" % (
                obj.redirectURL,
                obj.obj.url or obj.absolute_url(),
                obj.enableRegexURL)

    @property
    def redirect_to(self):
        return "policy-confirmation"

    @property
    def prefix(self):
        return schema_prefix

    def get_registry_entry(self,entry):
        _entry = None
        try:
            _entry = api.portal.get_registry_record(entry)
        except ComponentLookupError:
            pass
        return _entry

    def is_front_page(self):
        """
        Check if the viewlet is on a front page.
        Handle canonical paths correctly.
        based on docs:
        http://docs.plone.org/develop/plone/serving/traversing.html#checking-if-an-item-is-the-site-front-page
        """
        # Get path with "Default content item" wrapping applied
        context_helper = getMultiAdapter((self.context, self.request),
                                                 name="plone_context_state")
        canonical = context_helper.canonical_object()
        path = canonical.absolute_url_path()
        return INavigationRoot.providedBy(canonical)

    @ram.cache(lambda *args: time() // (60 * 60))
    def redirects(self):
        catalog = api.portal.get_tool('portal_catalog')
        redirects = catalog(portal_type='redirectpage')
        results = []
        for redirect in redirects:
            obj = redirect.getObject()
            obj.script = self.script(obj)
            results.append(obj)
        return results