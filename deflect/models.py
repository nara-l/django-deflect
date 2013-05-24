from __future__ import unicode_literals

import base64
from cStringIO import StringIO

import base32_crockford

import qrcode

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Django version < 1.5
    from django.contrib.auth.models import User


@python_2_unicode_compatible
class RedirectURL(models.Model):
    """
    A ``RedirectURL`` represents a redirection mapping between a short
    URL and the full destination URL. Several additional values are
    stored with related data and usage statistics.

    The short URL itself is not stored, but can be generated on demand
    using the ``short_url`` property.
    """
    campaign = models.CharField(_('campaign'), max_length=64, blank=True,
                                help_text=_('The individual campaign name, slogan, promo code, etc. for a product.'))
    content = models.CharField(_('content'), max_length=64, blank=True,
                               help_text=_('Used to differentiate similar content, or links within the same ad.'))
    created = models.DateTimeField(_('created'), auto_now_add=True, editable=False)
    description = models.TextField(_('description'), blank=True)
    hits = models.IntegerField(default=0, editable=False)
    last_used = models.DateTimeField(_('last used'), editable=False, blank=True, null=True)
    medium = models.CharField(_('medium'), max_length=64, blank=True,
                              help_text=_('The advertising or marketing medium, e.g.: cpc, banner, email newsletter.'))
    url = models.URLField(_('target url'), help_text=_('The full destination URL redirected to from the short URL.'))
    user = models.ForeignKey(User, verbose_name=_('user'), editable=False)

    class Meta:
        verbose_name = _('Redirect URL')
        verbose_name_plural = _('Redirect URLs')

    def __str__(self):
        return self.url

    @property
    def url_path(self):
        return base32_crockford.encode(self.pk)

    def get_absolute_url(self):
        return reverse('deflect.views.redirect', args=[self.url_path])

    def short_url(self):
        """
        Return the complete short URL for the current redirect.
        """
        url_base = 'http://%s' % Site.objects.get_current().domain
        return url_base + self.get_absolute_url()

    def qr_code(self):
        """
        Return an HTML img tag containing an inline base64 encoded
        representation of the short URL as a QR code.
        """
        png_stream = StringIO()
        img = qrcode.make(self.short_url())
        img.save(png_stream)
        png_base64 = base64.b64encode(png_stream.getvalue())
        png_stream.close()
        return '<img src="data:image/png;base64,%s" />' % png_base64
    qr_code.allow_tags = True
