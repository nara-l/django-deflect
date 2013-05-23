from __future__ import unicode_literals

import base32_crockford
import logging

from django.db.models import F
from django.http import Http404
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from .models import RedirectURL
from .utils import add_query_params


logger = logging.getLogger(__name__)


def redirect(request, url_path):
    """
    Given the path component of a short URL, update the URL's
    statistics and redirect the user to the full destination
    URL, including available Google Analytics parameters.
    """
    try:
        id = base32_crockford.decode(url_path)
    except ValueError as e:
        logger.warning("Error decoding redirect '%s': %s" % (url_path, e))
        raise Http404

    redirect = get_object_or_404(RedirectURL, pk=id)
    RedirectURL.objects.filter(pk=id).update(hits=F('hits') + 1,
                                             last_used=now())

    # Inject Google campaign parameters; if any of these
    # are not set, they will be ignored
    utm_params = {'utm_source': redirect.url_path,
                  'utm_campaign': redirect.campaign,
                  'utm_content': redirect.content,
                  'utm_medium': redirect.medium}
    url = add_query_params(redirect.url, utm_params)

    return HttpResponsePermanentRedirect(url)
