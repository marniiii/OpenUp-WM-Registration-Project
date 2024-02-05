class Cart():
    def __init__(self, request):
        self.session = request.session

        #get current session key if exists
        cart = self.session.get('session_key')

        #if new user, no session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        #make sure cart is available on all pages
            
        self.cart = cart

    def add(self, url, CRN, title):
    # Check if the CRN is already in the cart
        if CRN in self.cart:
            # If CRN is already in the cart, check if the URLs are different
            if self.cart[CRN]['URL'] != str(url):
                # URLs are different, handle it accordingly
                pass
        else:
            # If CRN is not in the cart or if it's in the cart with a different URL, add the item
            self.cart[CRN] = {'URL': str(url), 'CRN': str(CRN), 'TITLE': str(title)}

        self.session.modified = True

    def __len__(self):
        return len(self.cart)
    
    def get_classes(self):
        class_info = self.cart.values()  # Get a list of all items in the cart

    # Now 'class_info' is a list of dictionaries containing URL, CRN, and TITLE
        for class_item in class_info:
            crn = class_item['CRN']
            title = class_item['TITLE']
            
            # Do something with the CRN and title (e.g., print or store in a list)
            return crn, title