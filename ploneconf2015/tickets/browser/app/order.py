""" Order view
"""
import json
from decimal import Decimal
from zope.component import queryMultiAdapter
from Products.Five.browser import BrowserView

class Order(BrowserView):
    """ Order view
    """
    def __init__(self, context, request):
        super(Order, self).__init__(context, request)
        self._data = None

    @property
    def data(self):
        """ Data
        """
        if self._data is None:
            self._data = json.loads(self.context.data )
        return self._data

    @property
    def oid(self):
        """ Order id
        """
        return self.context.getId().split('-')[1]

    @property
    def subtotal(self):
        """ Subtotal price
        """
        cart = self.data.get('cart', [])
        return self.context.price_per_item * len(cart)

    @property
    def vat(self):
        """ Total VAT
        """
        cart = self.data.get('cart', [])
        return self.context.vat_per_item * len(cart)

    @property
    def pret(self):
        """ Total price in RON
        """
        return self.context.pret

    @property
    def tva(self):
        """ Total VAT in RON
        """
        return self.context.exchange_rate * self.vat

    @property
    def pret_net(self):
        """ Subtotal in RON
        """
        return self.pret - self.tva

    @property
    def date(self):
        """ Order date
        """
        date = self.context.creation_date
        return date.strftime('%d %b %Y')

    def render(self, amount, currency=u'\u20ac'):
        """ Render money
        """
        amount = Decimal('%.2f' % amount)
        if currency.lower() != 'ron':
            return u'%s%.2f' % (currency, amount)
        return u'%.2f %s' % (amount, currency)

class OrderPrint(BrowserView):
    """ Print order
    """
    def __call__(self, **kwargs):
        self.request.form['P_SIGN'] = self.context.p_sign
        support = queryMultiAdapter((self.context, self.request),
                                    name='pdf.support')
        email = getattr(support, 'email', lambda: None)()
        download = queryMultiAdapter((
            self.context, self.request), name='download.pdf')
        return download.download(email=email)
